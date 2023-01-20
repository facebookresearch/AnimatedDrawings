import os
os.environ['PYOPENGL_PLATFORM'] = "osmesa"
os.environ['MESA_GL_VERSION_OVERRIDE'] = "3.3"
from OpenGL import GL, osmesa

from animated_drawings.model.camera import Camera
from animated_drawings.model.scene import Scene
from animated_drawings.model.transform import Transform
from animated_drawings.view.view import View
from animated_drawings.view.utils import get_projection_matrix
from animated_drawings.utils import read_background_image
from animated_drawings.view.shaders.shader import Shader

import logging
from typing import Tuple
import numpy as np
from pathlib import Path
from pkg_resources import resource_filename


class MesaView(View):
    """ Mesa View for Headless Rendering """

    def __init__(self, cfg: dict):
        super().__init__(cfg)

        self.camera: Camera = Camera(cfg['CAMERA_POS'], cfg['CAMERA_FWD'])

        self.ctx: osmesa.OSMesaContext
        self.buffer: np.ndarray
        self._initialize_mesa()

        self.shaders = {}
        self.shader_ids = {}
        self._prep_shaders()

        if self.cfg['BACKGROUND_IMAGE']:
            self._prep_background_image()

        self._set_shader_projections(get_projection_matrix(*self.get_framebuffer_size()))

    def _prep_background_image(self):
        _txtr = read_background_image(self.cfg['BACKGROUND_IMAGE'])

        self.txtr_h, self.txtr_w, _ = _txtr.shape
        self.txtr_id = GL.glGenTextures(1)
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 4)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.txtr_id)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_BASE_LEVEL, 0)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAX_LEVEL, 0)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, self.txtr_w, self.txtr_h, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, _txtr)

        self.fboId: GL.GLint = GL.glGenFramebuffers(1)
        GL.glBindFramebuffer(GL.GL_READ_FRAMEBUFFER, self.fboId)
        GL.glFramebufferTexture2D(GL.GL_READ_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D, self.txtr_id, 0)

    def _prep_shaders(self):
        BVH_VERT = Path(resource_filename(__name__, "shaders/bvh.vert"))
        BVH_FRAG = Path(resource_filename(__name__, "shaders/bvh.frag"))
        self._initiatize_shader('bvh_shader', str(BVH_VERT), str(BVH_FRAG))

        COLOR_VERT = Path(resource_filename(__name__, "shaders/color.vert"))
        COLOR_FRAG = Path(resource_filename(__name__, "shaders/color.frag"))
        self._initiatize_shader('color_shader', str(COLOR_VERT), str(COLOR_FRAG))

        TEXTURE_VERT = Path(resource_filename(__name__, "shaders/texture.vert"))
        TEXTURE_FRAG = Path(resource_filename(__name__, "shaders/texture.frag"))
        self._initiatize_shader('texture_shader', str(TEXTURE_VERT), str(TEXTURE_FRAG), texture=True)

    def _update_shaders_view_transform(self, camera: Camera):
        try:
            view_transform: np.ndarray = np.linalg.inv(camera.get_world_transform())
        except Exception as e:
            msg = f'Error inverting camera world transform: {e}'
            logging.critical(msg)
            assert False, msg

        for shader_name in self.shaders:
            GL.glUseProgram(self.shader_ids[shader_name])
            view_loc = GL.glGetUniformLocation(self.shader_ids[shader_name], "view")
            GL.glUniformMatrix4fv(view_loc, 1, GL.GL_FALSE, view_transform.T)

    def _set_shader_projections(self, proj_m: np.ndarray):
        for shader_id in self.shader_ids.values():
            GL.glUseProgram(shader_id)
            proj_loc = GL.glGetUniformLocation(shader_id, "proj")
            GL.glUniformMatrix4fv(proj_loc, 1, GL.GL_FALSE, proj_m.T)

    def _initiatize_shader(self, shader_name: str, vert_path: str, frag_path: str, **kwargs):
        self.shaders[shader_name] = Shader(vert_path, frag_path)
        self.shader_ids[shader_name] = self.shaders[shader_name].glid

        if 'texture' in kwargs and kwargs['texture'] is True:
            GL.glUseProgram(self.shader_ids[shader_name])
            GL.glUniform1i(GL.glGetUniformLocation(
                self.shader_ids[shader_name], 'texture0'), 0)

    def _initialize_mesa(self):

        width, height = self.cfg['WINDOW_DIMENSIONS']
        self.ctx = osmesa.OSMesaCreateContext(osmesa.OSMESA_RGBA, None)
        self.buffer = GL.arrays.GLubyteArray.zeros((height, width, 4))  # type: ignore
        osmesa.OSMesaMakeCurrent(self.ctx, self.buffer, GL.GL_UNSIGNED_BYTE, width, height)

        GL.glClearColor(*self.cfg['CLEAR_COLOR'])

    def set_scene(self, scene: Scene):
        self.scene = scene

    def render(self, transform: Transform):
        GL.glViewport(0, 0, *self.get_framebuffer_size())

        # Draw the background
        if self.cfg['BACKGROUND_IMAGE']:
            GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, 0)
            GL.glBindFramebuffer(GL.GL_READ_FRAMEBUFFER, self.fboId)
            win_w, win_h = self.get_framebuffer_size()
            GL.glBlitFramebuffer(0, 0, self.txtr_w, self.txtr_h, 0, 0, win_w, win_h, GL.GL_COLOR_BUFFER_BIT, GL.GL_LINEAR)

        self._update_shaders_view_transform(self.camera)

        transform.draw(shader_ids=self.shader_ids, viewer_cfg=self.cfg)

    def get_framebuffer_size(self) -> Tuple[int, int]:
        """ Return (width, height) of view's window. """
        return self.buffer.shape[:2][::-1]

    def clear_window(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)  # type: ignore
