import os
from OpenGL import GL, osmesa
import cv2
import numpy as np
from SceneManager.base_manager import BaseManager


class RenderManager(BaseManager):

    def __init__(self, cfg=None, width=1920, height=1080):
        assert cfg is not None
        self.cfg = cfg
        self.width = width
        self.height = height

        self.mode = 'RENDER'
        self.render_fps = self.cfg['RENDER_FPS']
        self.render_idx = 0

        if not os.path.exists(self.cfg['OUTPUT_PATH']):
            os.mkdir(self.cfg['OUTPUT_PATH'])

        self.ctx = None
        self.buffer = None
        self._initialize_mesa(self.width, self.height)
        #self._initialize_opengl(self.width, self.height)  # uncomment, comment line above if no mesa available

        super().__init__(cfg)

    def run(self):
        self.time_manager.initialize_time()

        while not self._scene_is_finished():
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
            self._update_transferrer_cameras()

            self._adjust_sketch()

            self._render_view()

            self._update()

            self._render_to_file(self.cfg['OUTPUT_PATH'])

    def _render_to_file(self, dir):
        data = np.empty((self.height, self.width, 3), dtype='uint16')
        GL.glReadPixels(0, 0, self.width, self.height, GL.GL_RGB, GL.GL_UNSIGNED_SHORT, data)
        data = data[::-1, :, ::-1]  # turn rightside up, address cv2 BRG expectation
        cv2.imwrite(os.path.join(dir, "{:04}.png".format(self.render_idx)), data)
        self.render_idx += 1

    def _render_view(self):
        camera, bottom, left, width, height = self.camera_manager.free_camera, 0, 0, self.width, self.height

        GL.glViewport(left, bottom, width, height)  # set viewport

        view = self.camera_manager.get_view_matrix(camera)
        view_pos = self.camera_manager.get_camera_position(camera)
        for key in self.shader_ids:
            GL.glUseProgram(self.shader_ids[key])
            view_loc = GL.glGetUniformLocation(self.shader_ids[key], "view")
            GL.glUniformMatrix4fv(view_loc, 1, GL.GL_FALSE, view.T)
            viewPos_loc = GL.glGetUniformLocation(self.shader_ids[key], "viewPos")
            GL.glUniform3fv(viewPos_loc, 1, view_pos)

        for drawable in self.drawables:
            if camera.is_drawable_visible_in_camera(drawable):
                drawable.draw(shader_ids=self.shader_ids, time=self.time_manager.get_current_bvh_frame(), camera=camera)

    def _initialize_mesa(self, width: int, height: int):

        self.ctx = osmesa.OSMesaCreateContext(osmesa.OSMESA_RGBA, None)
        self.buffer = GL.arrays.GLubyteArray.zeros((height, width, 4))
        assert osmesa.OSMesaMakeCurrent( self.ctx, self.buffer, GL.GL_UNSIGNED_BYTE, width, height)
        assert osmesa.OSMesaGetCurrentContext()

        print('OpenGL', GL.glGetString(GL.GL_VERSION).decode() + ', GLSL',
              GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode() +
              ', Renderer', GL.glGetString(GL.GL_RENDERER).decode())

        GL.glClearColor(*self.cfg['CLEAR_COLOR'])
        GL.glEnable(GL.GL_CULL_FACE)
        if self.cfg['USE_DEPTH_TEST']:
            GL.glEnable(GL.GL_DEPTH_TEST)

        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA);

    def _initialize_opengl(self, width: int, height: int):
        import glfw
        glfw.init()
        """ Initalize opengl"""
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, False)

        self.win = glfw.create_window(width, height, 'Viewer', None, None)

        glfw.make_context_current(self.win)

        #glfw.set_key_callback(self.win, self._on_key)

        print('OpenGL', GL.glGetString(GL.GL_VERSION).decode() + ', GLSL',
              GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode() +
              ', Renderer', GL.glGetString(GL.GL_RENDERER).decode())

        GL.glClearColor(*self.cfg['CLEAR_COLOR'])
        GL.glEnable(GL.GL_CULL_FACE)
        if self.cfg['USE_DEPTH_TEST']:
            GL.glEnable(GL.GL_DEPTH_TEST)

        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA);

        #glfw.set_cursor_pos_callback(self.win, self._on_mouse_move)
        glfw.set_input_mode(self.win, glfw.CURSOR, glfw.CURSOR_DISABLED)


