from model.transform import Transform
from model.arap import ARAP, plot_mesh
from model.old_arap import old_ARAP
import yaml
import logging
import cv2
from pathlib import Path
import numpy as np
from skimage import measure
import ctypes
from scipy.spatial import Delaunay
from shapely import geometry
from typing import Dict, List, Optional
import OpenGL.GL as GL

# TODO: move joint from BVH into it's own file and then incorporate it from there
class Joint(Transform):

    def __init__(self):
        pass

class Rig(Transform):
    """ The skeletal rig used to deform the character """

    def __init__(self, char_cfg: Dict[str, dict]):
        """
        Initializes character rig in four steps:
        1 - Populate joint dictionary with joint transforms, using global image position of joint as initial local offset
        2 - Computes and add the root joint
        3 - Build skeletal hierarchy
        4 - Updates joint positions to reflect local offsets from their parent joints
        """
        super().__init__()

        # TODO: The following should be abstracted to a mapping, so we can eventually support other types of skeletons
        # TODO: Put this into a try clause to protect against bad user input
        # 1

        # TODO: These need to be children of the rig, not self.joints
        # TODO: 
        # but do have a special pointer to root
        self.joints: Dict[str, Transform] = {}
        for joint_d in char_cfg['skeleton']:
            joint_t = Transform(name=joint_d['name'])
            x, y = joint_d['loc']
            # 1 - y as textures are flipped
            joint_t.offset(np.array([x, 1 - y, 0]))
            self.joints[joint_d['name']] = joint_t

        # 2
        averaged_root_joints = ['left_hip', 'right_hip']  # TODO: values should be specified in config
        r_xyz: np.ndarray = np.mean(
            [self.joints[name].get_world_position() for name in averaged_root_joints], axis=0)
        root_t = Transform(name='root')
        root_t.offset(r_xyz)
        self.joints['root'] = root_t

        # 3
        for joint_d in char_cfg['skeleton']:
            if joint_d['parent'] is None:
                continue
            self.joints[joint_d['parent']].add_child(
                self.joints[joint_d['name']])

        # 4
        def _update_positions(t: Transform):
            parent: Optional[Transform] = t.get_parent()
            if parent is not None:
                offset = np.subtract(t.get_local_position(), parent.get_world_position())
                t.set_position(offset)
            for c in t.get_children():
                _update_positions(c)
        _update_positions(self.joints['root'])

        # (5) get vertices computed and ready for the gl buffer
        self.vertices = np.zeros([2*(len(self.joints)-1), 6], np.float32)

        self._is_opengl_initialized: bool = False
        self._vertex_buffer_dirty_bit: bool = True

    def _compute_buffer_vertices(self, parent: Optional[Transform], pointer: List[int]) -> None:
        """
        Recomputes values to pass to vertex buffer. Called recursively, pointer is List[int] to emulate pass-by-reference
        """
        if parent is None:
            parent = self.joints['root']

        for c in parent.get_children():
            p1 = c.get_world_position()
            p2 = parent.get_world_position()

            self.vertices[pointer[0], 0:3] = p1
            self.vertices[pointer[0]+1, 0:3] = p2
            pointer[0] += 2

            self._compute_buffer_vertices(c, pointer)

    def _initialize_opengl_resources(self):
        self.vao = GL.glGenVertexArrays(1)
        self.vbo = GL.glGenBuffers(1)

        GL.glBindVertexArray(self.vao)

        # buffer vertex data
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.vertices, GL.GL_STATIC_DRAW)

        vert_bytes = 4 * self.vertices.shape[1]  # 4 is byte size of np.float32

        pos_offset = 4 * 0
        color_offset = 4 * 3

        # position attributes
        GL.glVertexAttribPointer(
            0, 3, GL.GL_FLOAT, False, vert_bytes, ctypes.c_void_p(pos_offset))
        GL.glEnableVertexAttribArray(0)

        # color attributes
        GL.glVertexAttribPointer(
            1, 3, GL.GL_FLOAT, False, vert_bytes, ctypes.c_void_p(color_offset))
        GL.glEnableVertexAttribArray(1)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        self._is_opengl_initialized = True

    def _compute_and_buffer_vertex_data(self):

        self._compute_buffer_vertices(parent=self.joints['root'], pointer=[0])

        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.vertices, GL.GL_STATIC_DRAW)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        self._vertex_buffer_dirty_bit = False

    def get_joints_pos(self) -> np.ndarray:
        """
        Returns array of joints positions in local space of the rig
        """
        # step 1 get the world space coordinates of everything
        self.update_transforms()
        root = self.joints['root']  # TODO: eventually change this to be the rig itself
        #root_wt_i: np.ndarray = np.linalg.inv(root.get_world_transform())  # inverse of root's world transofrm
        #pos_list: list = self._get_joint_chain_relative_to(root, root_wt_i, [])

        pos_list: list = self._get_joint_chain_relative_to(root, np.identity(4), [])

        return np.array(pos_list)

    # TODO: move this into the joint class
    def _get_joint_chain_relative_to(self, joint: Transform, root_wt_i: np.ndarray, pos_list: List):
        """
        Recursively populates pos_list with xyz coordinates of joints in 'root' space, where parameter root_wt_i
        contains the inverse of the 'root's world transform.
        """
        # get the position of joints in joints chain relative to root position (world_transform)
        joint_wt: np.ndarray = joint.get_world_transform()
        joint_rt: np.ndarray = root_wt_i @ joint_wt  # joint transform wrt root
        pos_list.append(joint_rt[:-1, -1])
        for c in joint.get_children():
            self._get_joint_chain_relative_to(c, root_wt_i, pos_list)
        return pos_list

    def _draw(self, **kwargs):
        if not self._is_opengl_initialized:
            self._initialize_opengl_resources()
        
        if self._vertex_buffer_dirty_bit:
            self._compute_and_buffer_vertex_data()

        GL.glUseProgram(kwargs['shader_ids']['color_shader'])
        model_loc = GL.glGetUniformLocation(
            kwargs['shader_ids']['color_shader'], "model")
        GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE,
                              self.world_transform.T)

        GL.glBindVertexArray(self.vao)
        # GL.glDrawElements(GL.GL_TRIANGLES, 3, GL.GL_UNSIGNED_INT, ctypes.c_void_p(3 * 4))
        GL.glDrawArrays(GL.GL_LINES, 0, len(self.vertices))


class AnimatedDrawing(Transform):
    """
    The drawn character to be animated.
    It consists of a mesh and a 'rig' of as-rigid-as-possible control handles used to deform it.
    The character is 2D the mesh and rig both exist within the local XY plane at Z=0

    """

    def __init__(self, char_cfg_fn: str):
        super().__init__()

        self.char_cfg: dict = self._load_cfg(char_cfg_fn)

        self.img_dim = max(self.char_cfg['height'], self.char_cfg['width'])

        mask_fn = f'{Path(char_cfg_fn).parent}/{Path(char_cfg_fn).stem}_mask.png'
        self.mask: np.ndarray = self._load_mask(mask_fn)

        txtr_fn = f'{Path(char_cfg_fn).parent}/{Path(char_cfg_fn).stem}.png'
        self.txtr: np.ndarray = self._load_txtr(txtr_fn)

        self.mesh: dict = self._generate_mesh()
        self.vertices: np.ndarray = self._initialize_vertices()

        self.indices: np.ndarray = np.stack(self.mesh['triangles']).flatten()  # order in which to render triangles

        self.rig = Rig(self.char_cfg)
        self.add_child(self.rig)

        control_points: np.ndarray = self.rig.get_joints_pos()[:, :2] * self.img_dim
        self.arap = ARAP(control_points, self.mesh['triangles'], self.mesh['vertices'])
        #self.arap = old_ARAP(control_points, self.mesh['vertices'], np.stack(self.mesh['triangles']))

        #self.vertices[:, :2] = self.arap._arap_solve(control_points)[0].reshape([-1, 2]) / self.img_dim
        self.vertices[:, :2] = self.arap.solve(control_points)[0].reshape([-1, 2]) / self.img_dim


        #self.old_arap = old_ARAP(control_points[:, :2], self.mesh['vertices'], np.stack(self.mesh['triangles']))

        self._is_opengl_initialized: bool = False
        self._vertex_buffer_dirty_bit: bool = True

    def update(self):
        control_points: np.ndarray = self.rig.get_joints_pos()[:,:2] * self.img_dim

        self.vertices[:,:2] = self.arap.solve(control_points)[0].reshape([-1, 2]) / self.img_dim
        #self.vertices[:,:2] = self.arap._arap_solve(control_points)[0].reshape([-1, 2]) / self.img_dim

        #self.vertices[:,:2] = self.arap.solve(control_points) 
        self._vertex_buffer_dirty_bit = True

    def _load_cfg(self, cfg_fn: str) -> dict:
        try:
            with open(cfg_fn, 'r') as f:
                cfg = yaml.load(f, Loader=yaml.FullLoader)
        except Exception as e:
            msg = f'Error loading config {cfg_fn}: {str(e)}'
            logging.critical(msg)
            assert False, msg

        # scale joint locations to 0-1. txtr and mask will be padded to max_dim square
        max_dim = max(cfg['width'], cfg['height'])
        for joint in cfg['skeleton']:
            joint['loc'] = np.array(joint['loc']) / max_dim

        return cfg

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
        mask = np.zeros([self.img_dim, self.img_dim], _mask.dtype)
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
        txtr = np.zeros([self.img_dim, self.img_dim, _txtr.shape[-1]], _txtr.dtype)
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
        # TODO: Find a more prinicipled way to get a good mesh than sampling every 25 points prior to approximating?
        outside_vertices = measure.approximate_polygon(
            contours[0][::25,:], tolerance=0.25)
        character_outline = geometry.Polygon(outside_vertices)

        ## add some interal vertices to ensure a good mesh is created
        #inside_vertices = []
        #_x = np.linspace(0, self.img_dim, 20)
        #_y = np.linspace(0, self.img_dim, 20)
        #xv, yv = np.meshgrid(_x, _y)
        #for x, y in zip(xv.flatten(), yv.flatten()):
        #    if character_outline.contains(geometry.Point(x, y)):
        #        inside_vertices.append((x, y))
        #inside_vertices = np.array(inside_vertices)

        #vertices = np.concatenate([outside_vertices, inside_vertices])
        vertices = outside_vertices

        #plot_mesh([], [], vertices)
        """
        Create a convex hull containing the character.
        Then remove unnecessary edges by discarding triangles whose centroid
        falls outside the character's outline.
        """
        convex_hull_triangles = Delaunay(vertices)
        triangles = []
        #plot_mesh(vertices, convex_hull_triangles.simplices, [])
        for _triangle in convex_hull_triangles.simplices:
            tri_vertices = np.array(
                [vertices[_triangle[0]], vertices[_triangle[1]], vertices[_triangle[2]]])
            tri_centroid = geometry.Point(np.mean(tri_vertices, 0))
            if character_outline.contains(tri_centroid):
                triangles.append(_triangle)
        #plot_mesh(vertices, triangles, [])
        
        return {'vertices': vertices, 'triangles': triangles}

    def _initialize_vertices(self) -> np.ndarray:
        """ Prepare the ndarray that will be sent to rendering pipeline. Subsequenct calls will update the x and y pos of vertices,
        but z pos and u v textures won't change
        
        """
        vertices = np.empty((self.mesh['vertices'].shape[0], 5), np.float32)

        vertices[:, 0] = self.mesh['vertices'][:, 0] / self.img_dim    # x pos
        vertices[:, 1] = self.mesh['vertices'][:, 1] / self.img_dim    # y pos
        vertices[:, 2] = 0.0                                           # z pos
        vertices[:, 3] = self.mesh['vertices'][:, 1] / self.img_dim    # u tex
        vertices[:, 4] = self.mesh['vertices'][:, 0] / self.img_dim    # v tex

        return vertices

    def _initialize_opengl_resources(self) -> None:

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

    def _rebuffer_vertex_data(self):
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.vertices, GL.GL_STATIC_DRAW)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        self._vertex_buffer_dirty_bit = False

    def _draw(self, **kwargs):
        if not self._is_opengl_initialized:
            self._initialize_opengl_resources()

        if self._vertex_buffer_dirty_bit:
            self._rebuffer_vertex_data()

        GL.glBindVertexArray(self.vao)
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.txtr_id)

        # render texture
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        GL.glUseProgram(kwargs['shader_ids']['texture_shader'])
        model_loc = GL.glGetUniformLocation(
            kwargs['shader_ids']['texture_shader'], "model")
        GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE,
                              self.world_transform.T)
        GL.glDrawElements(
            GL.GL_TRIANGLES, self.indices.shape[0], GL.GL_UNSIGNED_INT, None)

        # # render mesh lines
        # GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
        # GL.glUseProgram(kwargs['shader_ids']['color_shader'])
        # model_loc = GL.glGetUniformLocation(kwargs['shader_ids']['color_shader'], "model")
        # GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE, self.world_transform.T)
        # GL.glDrawElements(GL.GL_TRIANGLES, self.indices.shape[0], GL.GL_UNSIGNED_INT, None)

        GL.glBindVertexArray(0)
