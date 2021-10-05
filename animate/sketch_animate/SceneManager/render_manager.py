import os
if 'SKETCH_ANIMATE_RENDER_BACKEND' in os.environ and \
        os.environ['SKETCH_ANIMATE_RENDER_BACKEND'] == 'OPENGL':
    from OpenGL import GL
    import glfw
else:
    from OpenGL import GL, osmesa

import cv2
import numpy as np
from SceneManager.base_manager import BaseManager
import logging
from pathlib import Path
import subprocess
import time


class RenderManager(BaseManager):

    def __init__(self, cfg=None, width=1080, height=1080):
        assert cfg is not None
        self.cfg = cfg
        self.width = width
        self.height = height

        self.mode = 'RENDER'
        self.video_fps = 18

        self.out_file = Path(os.path.join(self.cfg['OUTPUT_PATH']))

        # command line ffmpeg can't read and write to the same image, so create intermediate file and fix after
        self.intermediary_out_file = Path(str(self.out_file) + str(time.time()) + '.mp4')

        self.frame_data = np.empty([self.height, self.width, 3], dtype='uint8')
        self.frames_written = 0
        self.video_writer = None
        self.prep_video_writer()

        self.ctx = None
        self.buffer = None

        if 'SKETCH_ANIMATE_RENDER_BACKEND' in os.environ and \
        os.environ['SKETCH_ANIMATE_RENDER_BACKEND'] == 'OPENGL':
            self._initialize_opengl(self.width, self.height)  # uncomment, comment line above if no mesa available
        else:
            self._initialize_mesa(self.width, self.height)

        super().__init__(cfg)

    def prep_video_writer(self):

        os.makedirs(self.out_file.parent, exist_ok=True)

        if self.intermediary_out_file.exists():
            Path.unlink(self.intermediary_out_file)

        # cv2.videowriter can't use h264 to create mpegs,
        # so we're rendering with mp4v and later coverting to h264
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter(str(self.intermediary_out_file), fourcc, self.video_fps, (self.width, self.height))


    def run(self):
        self.time_manager.initialize_time()

        logging.info('starting render run')
        while not self._scene_is_finished():
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            self._update_transferrer_cameras()

            self._adjust_sketch()

            self._render_view()

            self._update()

            self._write_to_buffer()

        logging.info('render run completed')

        self.video_writer.release()

        self.convert_to_h264()

    def convert_to_h264(self):

        # delete old video file if exists
        if self.out_file.exists():
            Path.unlink(self.out_file)

        # mirror if cfg says so
        if self.cfg['MIRROR_CONCAT']:
            mirror_fn = Path(str(self.intermediary_out_file)+'_r.mp4')

            #mirror
            cmd = f'ffmpeg -r {self.video_fps} -i {str(self.intermediary_out_file)} -vf hflip {str(mirror_fn)}'
            subprocess.run(cmd.split(' '))

            #concat and convert to h264
            cmd = f'ffmpeg -r {self.video_fps} -i {str(self.intermediary_out_file)} -i {str(mirror_fn)} -filter_complex [0:v:0][1:v:0]concat=n=2:v=1[outv] -map [outv] {str(self.out_file)}'
            subprocess.run(cmd.split(' '))

            # clean up
            Path.unlink(self.intermediary_out_file)
            Path.unlink(mirror_fn)

        else:
            # convert to h264
            cmd = f'ffmpeg -r {self.video_fps} -i {str(self.intermediary_out_file)} -c:v h264 {str(self.out_file)}'
            subprocess.run(cmd.split(' '))

            # clean up
            Path.unlink(self.intermediary_out_file)


    def _write_to_buffer(self):
        # TODO: Joints pop between first and second frame. This is transferrer bug, but for now throw away first frame
        if not self.frames_written == 0:
            GL.glReadPixels(0, 0, self.width, self.height, GL.GL_BGR, GL.GL_UNSIGNED_BYTE, self.frame_data)
            self.video_writer.write(self.frame_data[::-1,:,:])
        self.frames_written += 1


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
        glfw.init()
        """ Initalize opengl"""
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, False)

        self.win = glfw.create_window(width, height, 'Viewer', None, None)

        glfw.make_context_current(self.win)

        print('OpenGL', GL.glGetString(GL.GL_VERSION).decode() + ', GLSL',
              GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode() +
              ', Renderer', GL.glGetString(GL.GL_RENDERER).decode())

        GL.glClearColor(*self.cfg['CLEAR_COLOR'])
        GL.glEnable(GL.GL_CULL_FACE)
        if self.cfg['USE_DEPTH_TEST']:
            GL.glEnable(GL.GL_DEPTH_TEST)

        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA);

        glfw.set_input_mode(self.win, glfw.CURSOR, glfw.CURSOR_DISABLED)


