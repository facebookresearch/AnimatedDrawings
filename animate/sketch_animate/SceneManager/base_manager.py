import OpenGL.GL as GL
import pyrr
from Shaders.Shader import Shader
from util import *
from camera import Camera
from time_manager import TimeManager
from transferrer import JointAngleTransferrer, RootMotionTransferrer
from Shapes.ARAP_Sketch import ARAP_Sketch
from camera_manager import CameraManager
from Shapes.BVH import BVH
import freetype as ft
from typing import List, Optional
import os
from abc import abstractmethod
import logging


class BaseManager:
    """ GLFW viewer window, with classic initialization & graphics loop """

    def __init__(self, cfg=None):
        assert cfg is not None

        # members associated with time and motion
        self.time_manager = TimeManager(cfg)
        self.loop_upper_limit = cfg['LOOP_REPEAT_UPPER_LIMIT']
        self.rendered_frame_upper_limit = cfg['RENDERED_FRAME_UPPER_LIMIT']
        self.x_position_upper_limit = cfg['X_POSITION_UPPER_LIMIT']

        self.joint_angle_transferrers = []
        self.root_motion_transferrer = None

        self.camera_manager = CameraManager(self)

        self.bvh = None
        self.sketch = None

        self.shaders = {}
        self.shader_ids = {}
        self.prep_shaders()

        self.drawables = []  # initially empty list of object to draw

    def prep_shaders(self):

        BVH_VERT = "../sketch_animate/Shaders/bvh.vert"
        BVH_FRAG = "../sketch_animate/Shaders/bvh.frag"
        self._initiatize_shader('bvh_shader', BVH_VERT, BVH_FRAG)

        COLOR_VERT = "../sketch_animate/Shaders/color.vert"
        COLOR_FRAG = "../sketch_animate/Shaders/color.frag"
        self._initiatize_shader('color_shader', COLOR_VERT, COLOR_FRAG)

        TEXTURE_VERT = "../sketch_animate/Shaders/texture.vert"
        TEXTURE_FRAG = "../sketch_animate/Shaders/texture.frag"
        self._initiatize_shader('texture_shader', TEXTURE_VERT, TEXTURE_FRAG, texture=True)

        GLYPH_VERT = "../sketch_animate/Shaders/glyph.vert"
        GLYPH_FRAG = "../sketch_animate/Shaders/glyph.frag"
        self._initiatize_shader('glyph_shader', GLYPH_VERT, GLYPH_FRAG)

        BORDER_VERT = "../sketch_animate/Shaders/border.vert"
        BORDER_FRAG = "../sketch_animate/Shaders/border.frag"
        self._initiatize_shader('border_shader', BORDER_VERT, BORDER_FRAG)

        POINTCLOUD_VERT = "../sketch_animate/Shaders/pointcloud.vert"
        POINTCLOUD_FRAG = "../sketch_animate/Shaders/pointcloud.frag"
        self._initiatize_shader('pointcloud_shader', POINTCLOUD_VERT, POINTCLOUD_FRAG)

        VECTOR_VERT = "../sketch_animate/Shaders/vector.vert"
        VECTOR_FRAG = "../sketch_animate/Shaders/vector.frag"
        self._initiatize_shader('vector_shader', VECTOR_VERT, VECTOR_FRAG)

        BONE_ASSIGN_VERT = "../sketch_animate/Shaders/bone_assignment.vert"
        BONE_ASSIGN_FRAG = "../sketch_animate/Shaders/bone_assignment.frag"
        self._initiatize_shader('bone_assignment', BONE_ASSIGN_VERT, BONE_ASSIGN_FRAG)


    @abstractmethod
    def run(self):
        pass

    def render_info_overlay(self):
        # render the frame number
        xpos = self.width / 2 - 150
        ypos = self.height / 2 - 30
        text = 'frame: {}'.format(self.time_manager.get_current_bvh_frame())
        color = [0, 0, 0]
        self.render_text(text, xpos, ypos, 1, color)

        # render the FPS
        xpos = self.width / 2 - 150
        ypos = self.height / 2 - 60
        text = 'FPS: {:.0f}'.format(self.time_manager.get_fps())
        color = [0, 0, 0]
        self.render_text(text, xpos, ypos, 1, color)

    def _adjust_sketch(self):

        if (self.time_manager.is_playing and self.cfg['CALCULATE_RENDER_ORDER']) or (
                self.mode == 'RENDER' and self.cfg['CALCULATE_RENDER_ORDER']):
            self.sketch.set_render_order(self.camera_manager.bvh_cameras[0], self.bvh,
                                         self.time_manager.get_current_bvh_frame())

        if self.cfg['SHOW_ORIGINAL_POSE_ONLY']:
            return

        for transferrer in self.joint_angle_transferrers:
            if transferrer.sketch is not None:
                transferrer.transfer_orientations(self.time_manager.get_current_bvh_frame())

        if self.root_motion_transferrer is not None:
            self.root_motion_transferrer.update_sketch_root_position(self.time_manager.get_current_bvh_frame())

    def _initialize_characters(self):
        # Load font  and check it is monotype
        filename = os.path.join(os.getcwd(), '..', 'fonts', 'VeraMono.ttf')
        size = 20
        face = ft.Face(filename)
        face.set_char_size(size * 64)
        if not face.is_fixed_width:
            raise Exception('Font is not monotype')

        for c in range(0, 128):
            face.load_char(c)

            texture = GL.glGenTextures(1)
            GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
            GL.glTexImage2D(
                GL.GL_TEXTURE_2D,
                0,
                GL.GL_RED,
                face.glyph.bitmap.width,
                face.glyph.bitmap.rows,
                0,
                GL.GL_RED,
                GL.GL_UNSIGNED_BYTE,
                face.glyph.bitmap.buffer
            )

            GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)  # necessary because we are using GL.GL_RED above

            # Set texture options
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

            character = self.Character(texture,
                                       np.array([face.glyph.bitmap.width, face.glyph.bitmap.rows], np.float32),
                                       np.array([face.glyph.bitmap_left, face.glyph.bitmap_top], np.float32),
                                       face.glyph.advance.x
                                       )
            self.characters[c] = character

        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        self.text_vao = GL.glGenVertexArrays(1)
        self.text_vbo = GL.glGenBuffers(1)
        GL.glBindVertexArray(self.text_vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.text_vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, 4 * 6 * 4, None,
                        GL.GL_DYNAMIC_DRAW)  # 2d quad requires 6 vertices of 4 float, each float is 4 bytes
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 4, GL.GL_FLOAT, False, 4 * 4, None)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def _set_shader_projections(self, proj_m: np.ndarray):
        for shader in self.shader_ids.values():
            GL.glUseProgram(shader)
            proj_loc = GL.glGetUniformLocation(shader, "proj")
            GL.glUniformMatrix4fv(proj_loc, 1, GL.GL_FALSE, proj_m.T)

    def _initiatize_shader(self, shader_name: str, vert_path: str, frag_path: str, texture=False, light=False):
        self.shaders[shader_name] = Shader(vert_path, frag_path)
        self.shader_ids[shader_name] = self.shaders[shader_name].glid

        if texture:
            GL.glUseProgram(self.shader_ids[shader_name])
            GL.glUniform1i(GL.glGetUniformLocation(self.shader_ids[shader_name], 'texture0'), 0)

    def _update(self):
        if self.time_manager.bvh is not None:
            self.time_manager.tick()

    def _scene_is_finished(self):
        """ Based upon contents of motion_config, determine if scene has finished playing"""
        if self.time_manager.loop_count >= self.loop_upper_limit:
            logging.info('self.time_manager.loop_count > self.loop_upper_limit. Scene is finished.')
            return True
        elif self.time_manager.cur_scene_frame > self.rendered_frame_upper_limit:
            logging.info('self.time_manager.cur_scene_frame > self.rendered_frame_upper_limit. Scene is finished.')
            return True
        elif self.sketch.joints['root'].local_matrix[0, -1] > self.x_position_upper_limit:
            logging.info('self.sketch.model[0, -1] > self.x_position_upper_limit. Scene is finished.')
            return True
        else:
            return False

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

    def add_free_camera(self, camera: Camera):  # TODO: Incorporate this
        """
        Sets the main camera. Used to extract sketch segment angles by the joint angle transferrers, and the initial viewport camera
        :param camera: camera to initially be used for viewport
        :return:
        """
        assert self.camera_manager.free_camera is None
        self.camera_manager.set_free_camera(camera)
        self.drawables.append(camera)
        self._set_shader_projections(
            self.camera_manager.get_proj_matrix(self.width, self.height, camera))  # TODO: This should go elsewhere

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

        transferrer = JointAngleTransferrer(self, self.cfg)
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

    def add_info_camera(self, camera: Camera):
        camera.initialize_target('root')
        self.camera_manager.add_info_camera(camera)

    def add_sketch_camera(self, camera: Camera):
        camera.initialize_target('root')
        self.camera_manager.set_sketch_camera(camera)

        for transferrer in self.joint_angle_transferrers:
            transferrer.view_camera = camera
        # self.drawables.append(camera)

    def add_test_camera(self, camera):
        camera.initialize_target('test')
        self.test_camera = camera
        self.camera_manager.add_bvh_camera(camera)
        self.drawables.append(camera)

    class Character:
        def __init__(self, _textureID, _size, _bearing, _advance):
            self.textureID = _textureID
            self.size = _size
            self.bearing = _bearing
            self.advance = _advance

    def render_text(self, text: str, x: int, y: int, scale: int, color: List[int]):
        shader_id = self.shader_ids['glyph_shader']

        GL.glUseProgram(shader_id)

        textColor_loc = GL.glGetUniformLocation(shader_id, "textColor")
        GL.glUniform3f(textColor_loc, color[0], color[1], color[2])

        projection = pyrr.matrix44.create_orthogonal_projection(-self.width / 2, self.width / 2, -self.height / 2,
                                                                self.height / 2, 1.0, 10.0).T
        projection_loc = GL.glGetUniformLocation(shader_id, "projection")
        GL.glUniformMatrix4fv(projection_loc, 1, GL.GL_FALSE, projection)

        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindVertexArray(self.text_vao)

        for c in text:
            ch = self.characters[ord(c)]

            xpos = x + ch.bearing[0] * scale
            ypos = y - (ch.size[1] - ch.bearing[1]) * scale

            w = ch.size[0] * scale
            h = ch.size[1] * scale

            vertices = np.array([
                [xpos, ypos + h, 0.0, 0.0],
                [xpos, ypos, 0.0, 1.0],
                [xpos + w, ypos, 1.0, 1.0],

                [xpos, ypos + h, 0.0, 0.0],
                [xpos + w, ypos, 1.0, 1.0],
                [xpos + w, ypos + h, 1.0, 0.0]
            ], np.float32)
            GL.glBindTexture(GL.GL_TEXTURE_2D, ch.textureID)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.text_vbo)

            GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, None, vertices)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
            GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)
            x += (ch.advance >> 6) * scale

        GL.glBindVertexArray(0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    def _update_retargetting_cameras(self):
        """
        updates position of bvh and sketch cameras
        called during the run loop
        :return:
        """
        frame_idx = self.time_manager.get_current_bvh_frame()
        root_pos = self.bvh.get_global_joint_position('root', frame_idx)
        root_forward = self.bvh.get_forward(frame_idx)

        self.camera_manager.set_bvh_cameras_target_position_and_forward(root_pos, root_forward)

        if self.camera_manager.sketch_camera is not None:
            sketch_root_pos = self.sketch.joints['root'].global_matrix[:-1, -1]
            self.camera_manager.set_sketch_camera_target_position(sketch_root_pos)

    def _update_transferrer_cameras(self):  # TODO: Rename this to include both transfer cameras and sketch cameras
        """
        updates position of transferrer cameras to follow the BVH.
        called during the run loop
        :return:
        """
        # get the position of the bvh root at this time step
        for transferrer in self.joint_angle_transferrers:  # TODO: See what happens if I remove this for loop.... this stuff should only be happening once

            # with the viewing angle, we get the position of the root joint for the target.
            # and we call the pca segmenter to get the optimal viewing angle.
            # Rotate the camera to the optimal viewing vector
            # translate it back a bit
            # then translate it to the root pos

            root_pos = transferrer.bvh.get_root_position(self.time_manager.get_current_bvh_frame())
            root_forward = transferrer.bvh.get_forward(self.time_manager.get_current_bvh_frame())
            transferrer.bvh_camera.set_target_position_and_forward(root_pos, root_forward)

        if self.camera_manager.sketch_camera is not None:
            sketch_root_pos = self.sketch.joints['root'].global_matrix[:-1, -1]
            self.camera_manager.set_sketch_camera_target_position(sketch_root_pos)

        for camera in self.camera_manager.info_cameras:
            sketch_root_pos = self.sketch.joints['root'].global_matrix[:-1, -1]
            camera.set_target_position(sketch_root_pos)
        # put in some code here to get the sketch root position and move the camera and orient it.
        # Also somewhere make it so you cannot move the camera with mouse and keyboard

    def create_root_motion_transferrer(self):
        """ Creates the transferrer responsible for sketch's root motion. both sketch and bvh must be set first"""
        assert self.bvh is not None
        assert self.sketch is not None

        assert self.root_motion_transferrer is None  # only one of these should exist

        self.root_motion_transferrer = RootMotionTransferrer(self.cfg, self.sketch, self.bvh)

    def add_sketch(self, sketch: ARAP_Sketch):
        """
        Adds the sketch to be animated to the viewer. Should only be called one
        :param sketch: Sketch object
        :return:
        """
        if self.sketch is not None:
            return

        for transferrer in self.joint_angle_transferrers:
            transferrer.set_sketch(sketch)

        self.sketch = sketch

        self.drawables.append(sketch)

    def add(self, drawable):
        """ add objects to draw in this window """
        self.drawables.append(drawable)
