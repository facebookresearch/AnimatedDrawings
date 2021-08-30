import glfw
import OpenGL.GL as GL
from Shader import Shader
from util import *
from ARAP import ARAP


class Viewer:

    def __init__(self, width=1500, height=800):
        self.width = width
        self.height = height

        self.win = None
        self._initialize_opengl(self.width, self.height)

        ##### prep shaders #####
        self.shaders = {}
        self.shader_ids = {}

        COLOR_VERT = "Shaders/color.vert"
        COLOR_FRAG = "Shaders/color.frag"
        self._initiatize_shader('color_shader', COLOR_VERT, COLOR_FRAG)

        TEXTURE_VERT = "Shaders/texture.vert"
        TEXTURE_FRAG = "Shaders/texture.frag"
        self._initiatize_shader('texture_shader', TEXTURE_VERT, TEXTURE_FRAG, texture=True)

        self.drawables = []

    def run(self):
        GL.glViewport(0, 0, self.width, self.height)
        """ Main render loop for this OpenGL window """
        while not glfw.window_should_close(self.win):
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            [drawable.draw(shader_ids=self.shader_ids) for drawable in self.drawables]

            glfw.swap_buffers(self.win)

            glfw.poll_events()

    def _initialize_opengl(self, width: int, height: int):
        """ Initalize opengl"""
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, False)

        self.win = glfw.create_window(width, height, 'Viewer', None, None)

        glfw.make_context_current(self.win)  # make win's OpenGL context current; no OpenGL calls can happen before

        glfw.set_key_callback(self.win, self._on_key)  # register event handlers

        # useful message to check OpenGL renderer characteristics
        print('OpenGL', GL.glGetString(GL.GL_VERSION).decode() + ', GLSL',
              GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode() +
              ', Renderer', GL.glGetString(GL.GL_RENDERER).decode())

        # initialize GL by setting viewport and default render characteristics
        GL.glClearColor(0.8, 0.8, 0.9, 0.1)

        GL.glEnable(GL.GL_BLEND)  # set up blending
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA);

        glfw.set_input_mode(self.win, glfw.CURSOR, glfw.CURSOR_DISABLED)

    def _initiatize_shader(self, shader_name: str, vert_path: str, frag_path: str, texture=False):
        self.shaders[shader_name] = Shader(vert_path, frag_path)
        self.shader_ids[shader_name] = self.shaders[shader_name].glid

        if texture:
            GL.glUseProgram(self.shader_ids[shader_name])
            GL.glUniform1i(GL.glGetUniformLocation(self.shader_ids[shader_name], 'texture0'), 0)

    def _on_key(self, _win, key: int, _scancode, action, _mods):

        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_ESCAPE or key == glfw.KEY_Q:
                glfw.set_window_should_close(self.win, True)
            elif key == glfw.KEY_W:
                self.arap.move_handle([0, -0.005])
                self.arap.arap_solve()
            elif key == glfw.KEY_S:
                self.arap.move_handle([0, 0.005])
                self.arap.arap_solve()
            elif key == glfw.KEY_A:
                self.arap.move_handle([-0.005, 0])
                self.arap.arap_solve()
            elif key == glfw.KEY_D:
                self.arap.move_handle([0.005, 0])
                self.arap.arap_solve()
            elif key == glfw.KEY_SPACE:
                self.arap.toggle_show_mesh_edges()
                self.arap.arap_solve()

    def add_arap(self, arap: ARAP):
        self.arap = arap
        self.drawables.append(arap)
