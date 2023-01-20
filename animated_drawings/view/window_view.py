from animated_drawings.view.view import View
from animated_drawings.view.shaders.shader import Shader
from animated_drawings.view.utils import get_projection_matrix
from animated_drawings.utils import read_background_image
from animated_drawings.model.scene import Scene
from animated_drawings.model.camera import Camera
from animated_drawings.model.transform import Transform
import glfw
import OpenGL.GL as GL
import logging
from typing import Tuple
import numpy as np
import os
from pathlib import Path
from pkg_resources import resource_filename


class WindowView(View):
    """Window View for rendering into a visible window"""

    def __init__(self, cfg: dict):
        super().__init__(cfg)

        glfw.init()

        self.camera: Camera = Camera(cfg['CAMERA_POS'], cfg['CAMERA_FWD'])
        self.win: glfw._GLFWwindow = self._create_window(*self.cfg['WINDOW_DIMENSIONS'])

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

    def _create_window(self, width: int, height: int):
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, False)

        win = glfw.create_window(width, height, 'Viewer', None, None)
        glfw.make_context_current(win)

        print('OpenGL', GL.glGetString(GL.GL_VERSION).decode() + ', GLSL',  # type: ignore
              GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode() +     # type: ignore
              ', Renderer', GL.glGetString(GL.GL_RENDERER).decode())        # type: ignore

        GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_DEPTH_TEST)

        # GL parameters specified by the cfg go here
        GL.glClearColor(*self.cfg['CLEAR_COLOR'])

        return win

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
        return glfw.get_framebuffer_size(self.win)

    def swap_buffers(self):
        glfw.swap_buffers(self.win)

    def clear_window(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)  # type: ignore
    
    def cleanup(self):
        """ Destroy the window when it's no longer being used. """
        glfw.destroy_window(self.win)
