import os
from util import use_opengl
import shutil

if use_opengl():
    from OpenGL import GL
    import glfw
else:
    from OpenGL import GL, osmesa

import cv2
import numpy as np
from SceneManager.base_manager import BaseManager
from pathlib import Path
import time
import ffmpeg
import multiprocessing as mp
from util import use_opengl
from time_manager import TimeManager_Render
from transferrer import Transferrer_Render


class RenderManager(BaseManager):

    def __init__(self, cfg=None, width=720, height=720):
        assert cfg is not None

        self.cfg = cfg
        self.width = width
        self.height = height

        if use_opengl():
            self._initialize_opengl(self.width, self.height)
        else:
            self._initialize_mesa(self.width, self.height)

        super().__init__(cfg)

        self.time_manager = None  # Transferrer_Render must be init prior- length of mocap sequence needed

        self.mode = 'RENDER'
        self.BVH_fps = 18  # cached motion files are all at 30 fps, but play at 18fps to look like flipbook

        if self.cfg['OUTPUT_PATH'].endswith('.mp4'):
            self.out_file = Path(os.path.join(self.cfg['OUTPUT_PATH']))
        else:
            vid_name = self.cfg['BVH_PATH'].split('/')[-1]
            self.out_file = Path(os.path.join(self.cfg['OUTPUT_PATH'])) / f'{vid_name}.mp4'

        self.video_working_dir = self.out_file.parent

        self.frame_data = np.empty([self.height, self.width, 3], dtype='uint8')
        self.frames_written = 0
        self.video_writer = None
        self.prep_video_writer()

        self.ctx = None
        self.buffer = None

    def prep_video_writer(self):

        os.makedirs(self.out_file.parent, exist_ok=True)

        if self.out_file.exists():
            Path.unlink(self.out_file)

        fourcc = cv2.VideoWriter_fourcc(*'x264')
        self.video_writer = cv2.VideoWriter(str(self.out_file), fourcc, self.BVH_fps, (self.width, self.height))

    def _is_frame_rendered(self, frame_idx):
        return frame_idx % 2

    def run(self):

        def do_drawing_stuff(vert_arr, frame_size, written, finished, mirror=False):
            pointer = 0

            while not finished[0] or not finished[1] or not finished[2] or written[pointer+1]:
                if not written[pointer+1]:
                    time.sleep(0.001)
                    continue

                mesh_vs = vert_arr[pointer*frame_size:(pointer+1)*frame_size]
                mesh_np = np.array(mesh_vs, dtype='float32')
                order = self.transferrer.ords[pointer % self.time_manager.bvh_frame_count]
                if self._is_frame_rendered(pointer):
                    self._render_view_mp(mesh_np, order, mirror)
                pointer += 1

        p_count = 3
        frame_size = 5 * self.sketch.nVertices
        arr_len = frame_size * self.cfg['RENDERED_FRAME_UPPER_LIMIT']
        vert_arr = mp.Array('f', arr_len)  # vertex info needed for rendering goes here
        finished = mp.Array('b', p_count) # array keeping track of whether a subprocess has finished yet
        written = mp.Array('b', arr_len)  # array keeping track of whether a frame has had its verts written yet

        sub_ps = []
        for idx, _ in enumerate(range(p_count)):
            p = mp.Process(target=self._compute_mesh_vertex_locs, args=(idx, p_count, vert_arr, frame_size, written, finished, self.sketch))
            sub_ps.append(p)

        [p.start() for p in sub_ps]

        do_drawing_stuff(vert_arr, frame_size, written, finished, mirror=False)

        [p.join() for p in sub_ps]

        if self.cfg['MIRROR_CONCAT']:
            do_drawing_stuff(vert_arr, frame_size, written, finished, mirror=True)

        self.video_writer.release()


    def create_transferrer_render(self):
        self.transferrer = Transferrer_Render(self, self.cfg)
        self.transferrer.set_motion_scale_factor(self.sketch)
        self.transferrer.prep_root_pos()

    def create_timemanager_render(self):
        self.time_manager = TimeManager_Render(self.cfg)

        frame_count = self.transferrer.rots.shape[0]
        self.time_manager.set_bvh_frame_count(frame_count)

    def _write_to_buffer(self, mirror=False):
        GL.glReadPixels(0, 0, self.width, self.height, GL.GL_BGR, GL.GL_UNSIGNED_BYTE, self.frame_data)
        frame = self.frame_data[::-1, :, :]
        if mirror:
            frame = frame[:, ::-1, :]
        self.video_writer.write(frame)
        self.frames_written += 1

    def _adjust_sketch(self):
        cur_bvh_frame = self.time_manager.get_current_bvh_frame()
        cur_scene_frame = self.time_manager.cur_scene_frame
        self.transferrer.retarget(self.sketch, cur_bvh_frame, cur_scene_frame)

    def _compute_mesh_vertex_locs(self, p_num, p_tot, vert_arr, frame_size, written, finished, sketch):
        frame_idx = p_num % p_tot
        while not self._scene_is_finished(frame_idx):
            if self._is_frame_rendered(frame_idx):
                self.transferrer.retarget(sketch, frame_idx % self.time_manager.bvh_frame_count, frame_idx)
                mv = sketch._arap_solve_render_mp()
                vert_arr[frame_idx*frame_size:(frame_idx+1)*frame_size] = mv.flatten()
                written[frame_idx] = True
                frame_idx += p_tot
            else:
                written[frame_idx] = True
                frame_idx += p_tot
        finished[p_num] = True
        return

    def _render_preamble(self):
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

    def _render_view_mp(self, mesh_vertices, order, mirror=False):
        self._render_preamble()
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        self.sketch.render_order = order

        camera = self.camera_manager.free_camera
        for drawable in self.drawables:
            if camera.is_drawable_visible_in_camera(drawable):
                if str(type(drawable)) == "<class 'Shapes.ARAP_Sketch.ARAP_Sketch'>":
                    drawable.draw_render_mp(mesh_vertices, shader_ids=self.shader_ids, time=self.time_manager.get_current_bvh_frame(), camera=camera)
                else:
                    drawable.draw(shader_ids=self.shader_ids, time=self.time_manager.get_current_bvh_frame(), camera=camera)

        self._write_to_buffer(mirror)

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


