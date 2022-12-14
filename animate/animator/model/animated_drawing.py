from model.transform import Transform
import yaml
import logging
import cv2
from pathlib import Path
import numpy as np
from skimage import measure
import ctypes
from scipy.spatial import Delaunay
from shapely import geometry
import OpenGL.GL as GL


class AnimatedDrawing(Transform):
    """ The drawn character to be animated. """

    def __init__(self, char_cfg_fn: str):
        super().__init__()

        self.char_cfg: dict = self._load_cfg(char_cfg_fn)

        mask_fn = f'{Path(char_cfg_fn).parent}/{Path(char_cfg_fn).stem}_mask.png'
        self.mask: np.ndarray = self._load_mask(mask_fn)

        txtr_fn = f'{Path(char_cfg_fn).parent}/{Path(char_cfg_fn).stem}.png'
        self.txtr: np.ndarray = self._load_txtr(txtr_fn)

        self.mesh: dict = self._generate_mesh()
        self.vertices: np.ndarray = self._generate_vertices()
        self.indices: np.ndarray = np.stack(self.mesh['triangles']).flatten()

        self._is_opengl_initialized: bool = False
        self._is_vertex_buffer_current: bool = False

    def _load_cfg(self, cfg_fn: str) -> dict:
        try:
            with open(cfg_fn, 'r') as f:
                return yaml.load(f, Loader=yaml.FullLoader)
        except Exception as e:
            msg = f'Error loading config {cfg_fn}: {str(e)}'
            logging.critical(msg)
            assert False, msg

    def _load_mask(self, mask_fn: str) -> np.ndarray:
        """ Load and perform preprocessing upon the mask """
        try:
            _mask = cv2.imread(mask_fn, cv2.IMREAD_GRAYSCALE)
            if _mask is None:
                raise ValueError('Could not read file')
            if _mask.shape[0] != self.char_cfg['height']:
                raise ValueError(
                    'height in character config and mask height do not match')
            if _mask.shape[1] != self.char_cfg['width']:
                raise ValueError(
                    'width in character config and mask height do not match')
        except Exception as e:
            msg = f'Error loading mask {mask_fn}: {str(e)}'
            logging.critical(msg)
            assert False, msg

        _mask = np.rot90(_mask, 3, )  # rotate to upright

        # pad to square
        max_dim = max(_mask.shape)
        mask = np.zeros([max_dim, max_dim], _mask.dtype)
        mask[0:_mask.shape[0], 0:_mask.shape[1]] = _mask

        return mask

    def _load_txtr(self, txtr_fn: str) -> np.ndarray:
        """ Load and perform preprocessing upon the drawing image """
        try:
            _txtr = cv2.imread(txtr_fn, cv2.IMREAD_IGNORE_ORIENTATION |
                               cv2.IMREAD_UNCHANGED).astype(np.float32)
            if _txtr is None:
                raise ValueError('Could not read file')
            if _txtr.shape[-1] != 4:
                raise TypeError('texture must be RGBA')
            if _txtr.shape[0] != self.char_cfg['height']:
                raise ValueError(
                    'height in character config and txtr height do not match')
            if _txtr.shape[1] != self.char_cfg['width']:
                raise ValueError(
                    'width in character config and txtr height do not match')
        except Exception as e:
            msg = f'Error loading texture {txtr_fn}: {str(e)}'
            logging.critical(msg)
            assert False, msg

        _txtr = np.rot90(_txtr, 3, )  # rotate to upright

        # pad to square
        max_dim = max(_txtr.shape)
        txtr = np.zeros([max_dim, max_dim, _txtr.shape[-1]], _txtr.dtype)
        txtr[0:_txtr.shape[0], 0:_txtr.shape[1], :] = _txtr

        # make pixels outside mask transparent
        txtr[np.where(self.mask == 0)] = 0

        return txtr

    def _generate_mesh(self):
        try:
            contours = measure.find_contours(self.mask, 128)
        except Exception as e:
            msg = f'Error finding contours for character mesh: {str(e)}'
            logging.critical(msg)
            assert False, msg

        # if multiple distinct polygons are in the mask, use largest and discard the rest
        if len(contours) > 1:
            msg = f'{len(contours)} separate polygons found in mask. Using largest.'
            logging.info(msg)
            contours.sort(key=len, reverse=True)

        # approximate polygon so resulting mesh has fewer triangles around edges
        outside_vertices = measure.approximate_polygon(
            contours[0], tolerance=0.25)

        character_outline = geometry.Polygon(outside_vertices)

        # add some interal vertices to ensure a good mesh is created
        inside_vertices = []
        _x = np.linspace(0, self.mask.shape[0], 20)
        _y = np.linspace(0, self.mask.shape[1], 20)
        xv, yv = np.meshgrid(_x, _y)
        for x, y in zip(xv.flatten(), yv.flatten()):
            if character_outline.contains(geometry.Point(x, y)):
                inside_vertices.append((x, y))
        inside_vertices = np.array(inside_vertices)

        vertices = np.concatenate([outside_vertices, inside_vertices])

        """
        Create a convex hull containing the character.
        Then remove unnecessary edges by discarding triangles whose centroid
        falls outside the character's outline.
        """
        convex_hull_triangles = Delaunay(vertices)
        triangles = []
        for _triangle in convex_hull_triangles.simplices:
            tri_vertices = np.array(
                [vertices[_triangle[0]], vertices[_triangle[1]], vertices[_triangle[2]]])
            tri_centroid = geometry.Point(np.mean(tri_vertices, 0))
            if character_outline.contains(tri_centroid):
                triangles.append(_triangle)

        return {'vertices': vertices, 'triangles': triangles}

    def _generate_vertices(self) -> np.ndarray:
        """ Prepare the ndarray that will be sent to rendering pipeline"""

        vertices = np.empty((self.mesh['vertices'].shape[0], 5), np.float32)

        _img_dim = self.txtr.shape[0]  # images are always padded to be square

        _vertices = np.stack(self.mesh['vertices'])

        vertices[:, 0] = _vertices[:, 0] / _img_dim     # x pos
        vertices[:, 1] = _vertices[:, 1] / _img_dim     # y pos
        vertices[:, 2] = 0.0                            # z pos
        vertices[:, 3] = _vertices[:, 1] / _img_dim     # x tex
        vertices[:, 4] = _vertices[:, 0] / _img_dim     # y tex

        return vertices

    def _initialize_opengl(self) -> None:

        h, w, _ = self.txtr.shape

        # # initialize the texture
        self.txtr_id = GL.glGenTextures(1)
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 4)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.txtr_id)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_BASE_LEVEL, 0)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAX_LEVEL, 0)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, w, h,
                        0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, self.txtr)

        self.vao = GL.glGenVertexArrays(1)
        self.vbo = GL.glGenBuffers(1)
        self.ebo = GL.glGenBuffers(1)

        GL.glBindVertexArray(self.vao)

        # buffer vertex data
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.vertices, GL.GL_DYNAMIC_DRAW)

        # buffer element index data
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER,
                        self.indices, GL.GL_STATIC_DRAW)

        # position attributes
        GL.glVertexAttribPointer(
            0, 3, GL.GL_FLOAT, False, 4 * self.vertices.shape[1], None)
        GL.glEnableVertexAttribArray(0)

        # texture attributes
        GL.glVertexAttribPointer(
            1, 2, GL.GL_FLOAT, False, 4 * self.vertices.shape[1], ctypes.c_void_p(4 * 3))
        GL.glEnableVertexAttribArray(1)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        self._is_opengl_initialized = True

    def _buffer_vertex_data(self):
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.vertices, GL.GL_STATIC_DRAW)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        self._is_vertex_buffer_current = True

    def _draw(self, **kwargs):
        if not self._is_opengl_initialized:
            self._initialize_opengl()

        if not self._is_vertex_buffer_current:
            self._buffer_vertex_data()

        GL.glBindVertexArray(self.vao)

        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.txtr_id)

        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)

        GL.glUseProgram(kwargs['shader_ids']['texture_shader'])
        model_loc = GL.glGetUniformLocation(
            kwargs['shader_ids']['texture_shader'], "model")

        GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE,
                              self.world_transform.T)

        GL.glDrawElements(
            GL.GL_TRIANGLES, self.indices.shape[0], GL.GL_UNSIGNED_INT, None)

        GL.glBindVertexArray(0)
