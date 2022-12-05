from abc import abstractmethod
from model.camera import Camera
import glfw
import OpenGL.GL as GL
from model.scene import Scene

import pyrr  # remove this


class View:

    def __init__(self, cfg: dict):
        self.cfg: dict = cfg
        pass

    @abstractmethod
    def render(self):
        pass


class InteractiveView(View):
    """Interactive View"""

    def __init__(self, cfg: dict, camera: Camera):
        super().__init__(cfg)
        self.camera: Camera = camera
        self.win: glfw._GLFWwindow = self._create_window(500, 500)

        self.proj_m = pyrr.matrix44.create_perspective_projection(35.0, 500 / 500, 0.1, 100.0).T  # remove pyrr dep

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

        GL.glClearColor(*self.cfg['CLEAR_COLOR'])
        GL.glEnable(GL.GL_CULL_FACE)
        if self.cfg['USE_DEPTH_TEST']:
            GL.glEnable(GL.GL_DEPTH_TEST)

        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        return win

    def render(self):
        GL.glViewport(0, 0, *glfw.get_framebuffer_size(self.win))

        self.scene._set_shader_projections(self.proj_m)
        # draw our scene objects
        # change this so that only try to draw something if it has a drawable component or something
        # also need to make this recursive-

        for child in self.scene.children:
            try:
                child.draw(shader_ids=self.scene.shader_ids)
            except Exception:
                pass

        # # Update each shader with the transform for this viewer's camera
        # view_transform = self.camera.transform
        # #view_pos = self.camera_manager.get_camera_position(camera)
        # for key in self.shader_ids:
        #     GL.glUseProgram(self.shader_ids[key])
        #     view_loc = GL.glGetUniformLocation(self.shader_ids[key], "view")
        #     GL.glUniformMatrix4fv(view_loc, 1, GL.GL_FALSE, view.T)
        #     viewPos_loc = GL.glGetUniformLocation(self.shader_ids[key], "viewPos")
        #     GL.glUniform3fv(viewPos_loc, 1, view_pos)

    def swap_buffers(self):
        glfw.swap_buffers(self.win)

    def clear_window(self):
        glfw.make_context_current(self.win)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)  # type: ignore
