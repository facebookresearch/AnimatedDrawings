from animator.view.view import View
from animator.view.shaders.shader import Shader
from animator.view.utils import get_projection_matrix
from animator.model.scene import Scene
from animator.model.camera import Camera
from animator.model.transform import Transform
import glfw
import OpenGL.GL as GL
import logging
from typing import Tuple
import numpy as np
import os
from pathlib import Path


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

        self._set_shader_projections(get_projection_matrix(*self.get_framebuffer_size()))

    def _prep_shaders(self):
        BVH_VERT = Path(os.environ['AD_ROOT_DIR'], "animate/animator/view/shaders/bvh.vert")
        BVH_FRAG = Path(os.environ['AD_ROOT_DIR'], "animate/animator/view/shaders/bvh.frag")
        self._initiatize_shader('bvh_shader', str(BVH_VERT), str(BVH_FRAG))

        COLOR_VERT = Path(os.environ['AD_ROOT_DIR'], "animate/animator/view/shaders/color.vert")
        COLOR_FRAG = Path(os.environ['AD_ROOT_DIR'], "animate/animator/view/shaders/color.frag")
        self._initiatize_shader('color_shader', str(COLOR_VERT), str(COLOR_FRAG))

        TEXTURE_VERT = Path(os.environ['AD_ROOT_DIR'], "animate/animator/view/shaders/texture.vert")
        TEXTURE_FRAG = Path(os.environ['AD_ROOT_DIR'], "animate/animator/view/shaders/texture.frag")
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

        self._update_shaders_view_transform(self.camera)

        transform.draw(shader_ids=self.shader_ids, viewer_cfg=self.cfg)

    def get_framebuffer_size(self) -> Tuple[int, int]:
        """ Return (width, height) of view's window. """
        return glfw.get_framebuffer_size(self.win)

    def swap_buffers(self):
        glfw.swap_buffers(self.win)

    def clear_window(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)  # type: ignore
