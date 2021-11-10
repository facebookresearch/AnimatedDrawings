from SceneManager.base_manager import BaseManager
import glfw
import OpenGL.GL as GL
from util import *
from Shapes.BVH import BVH
from transferrer import JointAngleTransferrer_Interact, RootMotionTransferrer
from camera import Camera
from typing import List, Optional
from time_manager import TimeManager_Interact

class InteractiveManager(BaseManager):

    def __init__(self, cfg=None, width=1500, height=800):
        glfw.init()
        assert cfg is not None
        self.cfg = cfg
        self.width = width
        self.height = height

        self.mode = 'INTERACT'

        self.win = None
        self._initialize_opengl(self.width, self.height)
        super().__init__(cfg)

        self.time_manager = TimeManager_Interact(self.cfg)    # Must be assigned by child class TimeManager(cfg)

        self.characters = {}
        self.text_vao = None
        self.text_vbo = None
        self._initialize_characters()

        self._initialize_borders()

        self.xpos, self.ypos = None, None  # mouse movement_variables

    def _initialize_opengl(self, width: int, height: int):
        """ Initalize opengl"""
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, False)

        self.win = glfw.create_window(width, height, 'Viewer', None, None)

        glfw.make_context_current(self.win)

        glfw.set_key_callback(self.win, self._on_key)

        print('OpenGL', GL.glGetString(GL.GL_VERSION).decode() + ', GLSL',
              GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode() +
              ', Renderer', GL.glGetString(GL.GL_RENDERER).decode())

        GL.glClearColor(*self.cfg['CLEAR_COLOR'])
        GL.glEnable(GL.GL_CULL_FACE)
        if self.cfg['USE_DEPTH_TEST']:
            GL.glEnable(GL.GL_DEPTH_TEST)

        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA);

        glfw.set_cursor_pos_callback(self.win, self._on_mouse_move)
        glfw.set_input_mode(self.win, glfw.CURSOR, glfw.CURSOR_DISABLED)

    def run(self):

        self.time_manager.initialize_time()

        while not glfw.window_should_close(self.win) and not self._scene_is_finished():
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            self._update_transferrer_cameras()

            self._adjust_sketch()

            self._render_views()

            self._update()

            if self.cfg['DRAW_INFO_OVERLAY']:
                self.render_info_overlay()

            glfw.swap_buffers(self.win)

            glfw.poll_events()

        glfw.terminate()

    def _on_key(self, _win, key: int, _scancode, action, _mods):
        if self.mode == 'RENDER':
            return

        if action == glfw.PRESS or action == glfw.REPEAT:

            if key == glfw.KEY_ESCAPE or key == glfw.KEY_Q:
                glfw.set_window_should_close(self.win, True)

            elif key == glfw.KEY_W:
                self.camera_manager.move_free_camera('forward')
                print(self.camera_manager.free_camera.pos, self.camera_manager.free_camera.yaw)
            elif key == glfw.KEY_S:
                print(self.camera_manager.free_camera.pos, self.camera_manager.free_camera.yaw)
                self.camera_manager.move_free_camera('backward')
            elif key == glfw.KEY_A:
                self.camera_manager.move_free_camera('left')
                print(self.camera_manager.free_camera.pos, self.camera_manager.free_camera.yaw)
            elif key == glfw.KEY_D:
                self.camera_manager.move_free_camera('right')
                print(self.camera_manager.free_camera.pos, self.camera_manager.free_camera.yaw)

            elif key == glfw.KEY_SPACE:
                self.time_manager.toggle_play()

            elif key == glfw.KEY_TAB:  # toggle through cameras in a list
                self.camera_manager.switch_cameras()
                glfw.set_window_title(self.win, self.camera_manager.cameras[0].name)
            elif key == glfw.KEY_T:
                toggle_camera_multi_view()
            elif key == glfw.KEY_G:
                toggle_mouse_mode()
                self._handle_mouse_mode_change(get_mouse_mode())

            elif key == glfw.KEY_P:
                toggle_sketch_segment_visibility()
            elif key == glfw.KEY_O:
                toggle_sketch_skeleton_visibility()
            elif key == glfw.KEY_L:
                toggle_arap_sketch_visibility()
            elif key == glfw.KEY_K:
                toggle_sketch_mesh_visibility()
            elif key == glfw.KEY_J:
                toggle_arap_handles_visibility()

            elif key == glfw.KEY_LEFT:
                self.time_manager.decrement_frame()
            elif key == glfw.KEY_RIGHT:
                self.time_manager.increment_frame()
            elif key == glfw.KEY_1:
                self.time_manager.set_inc_dec_step_size(1)
            elif key == glfw.KEY_2:
                self.time_manager.set_inc_dec_step_size(2)
            elif key == glfw.KEY_3:
                self.time_manager.set_inc_dec_step_size(3)
            elif key == glfw.KEY_4:
                self.time_manager.set_inc_dec_step_size(4)
            elif key == glfw.KEY_5:
                self.time_manager.set_inc_dec_step_size(5)

    def _handle_mouse_mode_change(self, new_mode):
        if new_mode == 'MOVE_CAMERA':
            glfw.set_input_mode(self.win, glfw.CURSOR, glfw.CURSOR_DISABLED)
            self.xpos, self.ypos = None, None
        elif new_mode == 'SELECTION':
            glfw.set_input_mode(self.win, glfw.CURSOR, glfw.CURSOR_NORMAL)

    def _on_mouse_move(self, win, xpos: float, ypos: float):
        if get_mouse_mode() == 'SELECTION':
            return

        if self.mode == 'RENDER':
            return

        if self.xpos is None:
            self.xpos = xpos
        if self.ypos is None:
            self.ypos = ypos

        self.camera_manager.free_camera.process_mouse_movement(xpos - self.xpos, ypos - self.ypos)
        self.ypos = ypos
        self.xpos = xpos

    def _render_views(self):
        for data in self.get_rendering_subwindow_info():
            camera, bottom, left, width, height, camera_name = data  # get the camera and viewport data
            GL.glViewport(left, bottom, width, height)  # set viewport

            # set and update uniforms for this particular camera
            view = self.camera_manager.get_view_matrix(camera)
            view_pos = self.camera_manager.get_camera_position(camera)
            for key in self.shader_ids:
                GL.glUseProgram(self.shader_ids[key])
                view_loc = GL.glGetUniformLocation(self.shader_ids[key], "view")
                GL.glUniformMatrix4fv(view_loc, 1, GL.GL_FALSE, view.T)
                viewPos_loc = GL.glGetUniformLocation(self.shader_ids[key], "viewPos")
                GL.glUniform3fv(viewPos_loc, 1, view_pos)

            # draw our scene objects
            for drawable in self.drawables:
                if camera.is_drawable_visible_in_camera(drawable):
                    drawable.draw(shader_ids=self.shader_ids, time=self.time_manager.get_current_bvh_frame(), camera=camera)

            # draw camera titles
            if self.cfg['DRAW_CAMERA_NAMES']:
                self.render_text(camera_name, 0, self.height / 2 - 50, 1, [0.0, 0.0, 0.0])

            # draw border
            self._draw_border()

    def add_bvh(self, bvh: BVH):
        """
        Adds the BVH used to drive the sketch animation into the scene. Should only be called once.
        :param bvh:
        :return:
        """
        if self.bvh is not None:
            return

        for transferrer in self.joint_angle_transferrers:
            transferrer.set_bvh(bvh)

        self.bvh = bvh

        self.time_manager.initialize_bvh(bvh)

        self.drawables.append(bvh)

    def add_bvh_camera(self, camera: Camera, target_segments: Optional[List[str]] = None):
        """
        given a camera and a list of target joints (and optional camera name), will create a joint angle transferrer that will adjust segments of the sketch
        based on how mocap bones are oriented, when projected on that camera.
        :param camera: the camera whose screen coordinates will be used to drive the joints
        :param target_segments: the joints of the sketch that will be driven by this transfer camera
        :param camera_name : camera name for display purposes
        :return:
        """
        camera.initialize_target('root')
        self.camera_manager.add_bvh_camera(camera)

        transferrer = JointAngleTransferrer_Interact(self, self.cfg)
        transferrer.set_bvh_camera(camera)
        transferrer.set_target_segments(target_segments)
        if self.camera_manager.sketch_camera is not None:
            transferrer.set_view_camera(self.camera_manager.sketch_camera)
        if self.bvh is not None:
            transferrer.set_bvh(self.bvh)
        if self.sketch is not None:
            transferrer.set_sketch(self.sketch)
        self.joint_angle_transferrers.append(transferrer)

        self.drawables.append(camera)
        self.drawables.append(transferrer)

    def _adjust_sketch(self):

        if (self.time_manager.is_playing and self.cfg['CALCULATE_RENDER_ORDER']):
            self.sketch.set_render_order(self.camera_manager.bvh_cameras[0],
                                         self.bvh,
                                         self.time_manager.get_current_bvh_frame())

            with open(self.cfg['OUTPUT_PATH'] + f'/{self.cfg["BVH_PATH"].split("/")[-1]}_render_order.txt', 'a') as f:
                f.write(str(self.sketch.render_order) + '\n')



        if self.cfg['SHOW_ORIGINAL_POSE_ONLY']:
            return

        for transferrer in self.joint_angle_transferrers:
            if transferrer.sketch is not None:
                transferrer.transfer_orientations(self.time_manager.get_current_bvh_frame())

        if self.root_motion_transferrer is not None:
            self.root_motion_transferrer.update_sketch_root_position(self.time_manager.get_current_bvh_frame())

    def create_root_motion_transferrer(self):
        """ Creates the transferrer responsible for sketch's root motion. both sketch and bvh must be set first"""
        assert self.bvh is not None
        assert self.sketch is not None

        assert self.root_motion_transferrer is None  # only one of these should exist

        self.root_motion_transferrer = RootMotionTransferrer(self.cfg, self.sketch, self.bvh, self)

    def get_rendering_subwindow_info(self):

        win_width, win_height = glfw.get_window_size(self.win)

        # for high res monitors (like macbook pro), must adjust for content scale
        csx, csy = glfw.get_monitor_content_scale(glfw.get_monitors()[0])
        win_width *= csx
        win_height *= csy

        ret = []

        if self.cfg['SHOW_MULTI_CAMERAS']:
            # assert len(self.cameras) == 4
            subwindow_width = int(win_width / 3)
            subwindow_height = int(win_height / 3)
            for idx, camera in enumerate(self.camera_manager.cameras):
                if idx == 0:
                    data = (camera, 0, 0, subwindow_width * 2, subwindow_height * 2,
                            camera.name)  # camera, bottom, left, width, height
                else:
                    if idx < 4:
                        y_offset = 2 * subwindow_height
                        x_offset = idx % 3 * subwindow_width
                    else:
                        y_offset = (5 - idx) % 3 * subwindow_height
                        # print(y_offset)
                        x_offset = 2 * subwindow_width
                    # if idx == 0:
                    #    y_offset = 0
                    #    x_offset = 0
                    # elif idx == 1:
                    #    y_offset = subwindow_height * idx
                    #    x_offset = 0
                    # elif idx == 2:
                    #    y_offset = 0
                    #    x_offset = subwindow_width
                    # elif idx == 3:
                    #    y_offset = subwindow_height
                    #    x_offset = subwindow_width
                    # else:
                    #    continue

                    data = (camera, y_offset, x_offset, subwindow_width, subwindow_height,
                            camera.name)  # camera, bottom, left, width, height
                ret.append(data)

            # large version of the main camera
            # ret.append((self.viewport_camera, 0, subwindow_width, win_width - subwindow_width, win_height - subwindow_height, self.viewport_camera.name))
        else:
            ret.append((self.camera_manager.free_camera, 0, 0, int(win_width), int(win_height), self.camera_manager.free_camera.name))

        return ret

    def _initialize_borders(self):
        from Shapes.Shapes import Border as Border
        self.borders = []
        self.borders.append(Border())

    def _draw_border(self):
        for rect in self.borders:
            rect.draw(shader_ids=self.shader_ids)

