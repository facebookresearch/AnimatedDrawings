from view.view import View
from model.camera import Camera
import glfw
import OpenGL.GL as GL
from model.scene import Scene
from model.transform import Transform

import pyrr  # # TODO remove this

from view.shaders.shader import Shader
import numpy as np


class InteractiveView(View):
    """Interactive View"""

    def __init__(self, cfg: dict, camera: Camera):
        super().__init__(cfg)
        self.camera: Camera = camera
        self.win: glfw._GLFWwindow = self._create_window(500, 500)

        # this should probably go into view
        self.shaders = {}
        self.shader_ids = {}
        self._prep_shaders()

        self._set_shader_projections(self._get_projection_matrix())

    def _get_projection_matrix(self):
        w_h: tuple[int, int] = glfw.get_framebuffer_size(self.win)
        return pyrr.matrix44.create_perspective_projection(35.0, w_h[0] / w_h[1], 0.1, 100.0).T  # TODO remove

    def _prep_shaders(self):

        BVH_VERT = "view/shaders/bvh.vert"
        BVH_FRAG = "view/shaders/bvh.frag"
        self._initiatize_shader('bvh_shader', BVH_VERT, BVH_FRAG)

        COLOR_VERT = "view/shaders/color.vert"
        COLOR_FRAG = "view/shaders/color.frag"
        self._initiatize_shader('color_shader', COLOR_VERT, COLOR_FRAG)

        TEXTURE_VERT = "view/shaders/texture.vert"
        TEXTURE_FRAG = "view/shaders/texture.frag"
        self._initiatize_shader('texture_shader', TEXTURE_VERT, TEXTURE_FRAG, texture=True)

    def update_shaders_view_transform(self, camera: Camera):
        view_transform: np.ndarray = camera.transform
        # TODO use self.shaders instead of self.shader_ids
        for key in self.shader_ids:
            GL.glUseProgram(self.shader_ids[key])
            view_loc = GL.glGetUniformLocation(self.shader_ids[key], "view")
            GL.glUniformMatrix4fv(view_loc, 1, GL.GL_FALSE, view_transform.T)
            viewPos_loc = GL.glGetUniformLocation(
                self.shader_ids[key], "viewPos")
            GL.glUniform3fv(viewPos_loc, 1, view_transform[-1:, :-1])

    # this should probably go into view
    def _set_shader_projections(self, proj_m: np.ndarray):
        # TODO use self.shaders instead of self.shader_ids
        for shader in self.shader_ids.values():
            GL.glUseProgram(shader)
            proj_loc = GL.glGetUniformLocation(shader, "proj")
            GL.glUniformMatrix4fv(proj_loc, 1, GL.GL_FALSE, proj_m.T)

    # this should probably go into view
    def _initiatize_shader(self, shader_name: str, vert_path: str, frag_path: str, **kwargs):
        self.shaders[shader_name] = Shader(vert_path, frag_path)
        self.shader_ids[shader_name] = self.shaders[shader_name].glid

        if 'texture' in kwargs and kwargs['texture'] is True:
            GL.glUseProgram(self.shader_ids[shader_name])
            GL.glUniform1i(GL.glGetUniformLocation(
                self.shader_ids[shader_name], 'texture0'), 0)

    def set_scene(self, scene: Scene):
        self.scene = scene

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
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        # GL parameters specified by the cfg go here 
        GL.glClearColor(*self.cfg['CLEAR_COLOR'])
        if self.cfg['USE_DEPTH_TEST']:
            GL.glEnable(GL.GL_DEPTH_TEST)

        return win

    def render(self, transform: Transform):
        GL.glViewport(0, 0, *glfw.get_framebuffer_size(self.win))

        self.update_shaders_view_transform(self.camera)

        transform.draw(shader_ids=self.shader_ids)

    def swap_buffers(self):
        glfw.swap_buffers(self.win)

    def clear_window(self):
        glfw.make_context_current(self.win)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)  # type: ignore
