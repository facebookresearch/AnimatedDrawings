from util import rotate, z_ax, x_ax, angle_from, normalized, constrain_angle
import numpy as np
from Shapes.Shapes import ScreenSpaceSquare
from camera import Camera

from typing import List
from Shapes.Sketch import Sketch

"""
Transferrers are responsible for transferring motion from the BVH onto the sketch. 
RootMotionTransferrer is responsible for transferring global translation onto the sketch.
JointAngleTransferrer are responsible determining the orientation of the BVH bones, when viewed from a particular direction,
and orientating a set of sketch bones such that, when the are viewed from a second camera, the orientation in screen space is identical.
"""


class Transferrer:

    def __init__(self):
        self.sketch = None
        self.bvh = None

    def set_sketch(self, sketch):
        self.sketch = sketch

    def set_bvh(self, bvh):
        self.bvh = bvh


class JointAngleTransferrer(Transferrer):
    def __init__(self, viewer, cfg):
        self.cfg = cfg
        self.bvh_camera = None
        self.target_joints = None
        self.view_camera = None
        self.viewer = viewer

        self.djnt_square = ScreenSpaceSquare(0, 0)
        self.pjnt_square = ScreenSpaceSquare(0, 0)

    def set_bvh_camera(self, camera: Camera):
        self.bvh_camera = camera

    def set_view_camera(self, camera: Camera):
        self.view_camera = camera

    def set_target_segments(self, target_segments: List[str]):
        self.target_joints = target_segments

    def transfer_orientations(self, time: int):
        """
        For every segment that this transferrer drives, compute the orientation
        using the screen coordinates of the driving joints
        """
        for segment in self.sketch.segments.values():
            if segment.name not in self.target_joints:
                continue

            proj_m = self.bvh_camera.get_proj_matrix(self.viewer.width, self.viewer.height)
            view_m = self.bvh_camera.get_view_matrix()

            bvh_bone_vector = normalized(self.get_bvh_bone_vector(segment, time, proj_m, view_m))
            theta = angle_from(x_ax, bvh_bone_vector)
            self.set_sketch_angle(segment, theta)


    def get_bvh_bone_vector(self, sketch_segment: Sketch.Segment, time: int, proj_m: np.array, view_m: np.array):
        """Given a segment(bone) and timeframe, returns the screenspace orientation of
        that bone. proj_m and view_m are calculated once and passed from calling function `transfer_orientations`
        since it is expensive
        """

        def name_to_screen_coords(seg_jnt_name: str):
            bvh_jnt_name = self.bvh.jnt_map[seg_jnt_name]
            idx = self.bvh.joint_names.index(bvh_jnt_name)
            pos = self.bvh.pos[time, idx, :]
            pos = np.array([*pos, 1.0], np.float32)

            screen = proj_m @ view_m @ self.bvh.model @ pos
            screen = screen[0:2] / screen[3]
            return screen


        djnt_screen = name_to_screen_coords(sketch_segment.dist_joint.name)
        pjnt_screen = name_to_screen_coords(sketch_segment.prox_joint.name)

        if sketch_segment.name == 'torso':
            self.set_djnt_screenspacesquare(*djnt_screen)
            self.set_pjnt_screenspacesquare(*pjnt_screen)

        return djnt_screen - pjnt_screen

    def set_djnt_screenspacesquare(self, x: float, y: float):
        self.djnt_square.update_position(x, y)

    def set_pjnt_screenspacesquare(self, x: float, y: float):
        self.pjnt_square.update_position(x, y)

    def get_sketch_bone_vector(self, sketch_segment: Sketch.Segment):

        def sketch_to_screen_coords(joint: Sketch.Joint):
            pos = joint.global_matrix[:, -1]
            screen = self.view_camera.get_proj_matrix(self.viewer.width,
                                                      self.viewer.height) @ self.view_camera.get_view_matrix() @ pos
            screen = (screen[0:2] / screen[3] + 1.0) / 2.0
            return screen

        djnt_screen = sketch_to_screen_coords(sketch_segment.dist_joint)
        pjnt_screen = sketch_to_screen_coords(sketch_segment.prox_joint)

        return djnt_screen - pjnt_screen

    def set_sketch_angle(self, sketch_segment: Sketch.Segment, theta: float):
        """Given a sketch segment, sets it's matrix so that it is theta degrees from the x axis"""
        pjnt_name = sketch_segment.prox_joint.name
        pjnt = self.sketch.joints[pjnt_name]
        djnt_name = sketch_segment.dist_joint.name
        djnt = self.sketch.joints[djnt_name]

        cur_theta = angle_from(x_ax, normalized(djnt.global_matrix[0:2, -1] - pjnt.global_matrix[0:2, -1]))
        delta = theta - cur_theta

        rmat = rotate(z_ax, delta)

        pjnt.local_matrix = pjnt.local_matrix @ rmat
        self.sketch._update_global_matrices()

    def draw(self, **kwargs):
        if self.cfg['DRAW_TRANSFERER_SSS']:
            self.djnt_square.draw(**kwargs)
            self.pjnt_square.draw(**kwargs)


class RootMotionTransferrer(Transferrer):

    def __init__(self, cfg, sketch, bvh):
        self.cfg = cfg
        self.sketch = sketch
        self.bvh = bvh
        self.sketch_root = self.sketch.joints['root']

        self.last_transferred_frame = 0

        self.motion_scaling_factor = None
        self._calculate_motion_scaling_factor()

        # cache forward root velocities for each frame
        frame_count = self.bvh.frame_count
        self.bvh_fwd_vel = np.empty([frame_count], np.float32)
        self.bvh_vrt_vel = np.empty([frame_count], np.float32)
        self._cache_bvh_root_velocities()

        self.sketch_positions = np.zeros([frame_count, 2], np.float32)  # [x positions, y position]
        self._cache_sketch_root_positions()

    def _cache_sketch_root_positions(self):
        for frame in range(1, self.bvh_fwd_vel.shape[0]):  # for every frame
            self.sketch_positions[frame, 0] = self.sketch_positions[frame - 1, 0] + self.motion_scaling_factor * \
                                              self.bvh_fwd_vel[frame]
            self.sketch_positions[frame, 1] = self.sketch_positions[frame - 1, 1] + self.motion_scaling_factor * \
                                              self.bvh_vrt_vel[frame]

    def _cache_bvh_root_velocities(self):
        self.bvh_fwd_vel[0] = 0.0
        self.bvh_vrt_vel[0] = 0.0
        root_pos = self.bvh.pos[:, 0, :]
        for frame in range(1, self.bvh_fwd_vel.shape[0]):
            old_pos = root_pos[frame - 1, :]
            new_pos = root_pos[frame, :]
            vel = new_pos - old_pos

            fwd = self.bvh.get_forward(frame)
            fwd_vel = np.dot(vel, fwd) / np.linalg.norm(fwd)
            self.bvh_fwd_vel[frame] = fwd_vel

            vrt_vel = vel[1]
            self.bvh_vrt_vel[frame] = vrt_vel

    def _calculate_motion_scaling_factor(self):
        """
        Calculate the amount the bvh's root velocity
        must be scaled to match the sketch. Do this by
        computing ratio of leg lengths, for now.
        """
        # bvh
        l_hip = self.bvh.pos[0, self.bvh.joint_names.index(self.bvh.jnt_map['left_hip']), :]
        l_knee = self.bvh.pos[0, self.bvh.joint_names.index(self.bvh.jnt_map['left_knee']), :]
        l_foot = self.bvh.pos[0, self.bvh.joint_names.index(self.bvh.jnt_map['left_foot']), :]
        l_leg_len = np.linalg.norm(l_hip - l_knee) + np.linalg.norm(l_knee - l_foot)

        r_hip = self.bvh.pos[0, self.bvh.joint_names.index(self.bvh.jnt_map['right_hip']), :]
        r_knee = self.bvh.pos[0, self.bvh.joint_names.index(self.bvh.jnt_map['right_knee']), :]
        r_foot = self.bvh.pos[0, self.bvh.joint_names.index(self.bvh.jnt_map['right_foot']), :]
        r_leg_len = np.linalg.norm(r_hip - r_knee) + np.linalg.norm(r_knee - r_foot)

        bvh_leg_length = l_leg_len + r_leg_len

        # sketch
        l_hip_pos = self.sketch.joints['left_hip'].global_matrix[0:3, -1]
        l_knee_pos = self.sketch.joints['left_knee'].global_matrix[0:3, -1]
        l_foot_pos = self.sketch.joints['left_foot'].global_matrix[0:3, -1]
        l_leg_len = np.linalg.norm(l_hip_pos - l_knee_pos) + np.linalg.norm(l_knee_pos - l_foot_pos)

        r_hip_pos = self.sketch.joints['right_hip'].global_matrix[0:3, -1]
        r_knee_pos = self.sketch.joints['right_knee'].global_matrix[0:3, -1]
        r_foot_pos = self.sketch.joints['right_foot'].global_matrix[0:3, -1]
        r_leg_len = np.linalg.norm(r_hip_pos - r_knee_pos) + np.linalg.norm(r_knee_pos - r_foot_pos)

        sketch_leg_length = l_leg_len + r_leg_len

        self.motion_scaling_factor = float(sketch_leg_length) / bvh_leg_length

    def update_sketch_root_position(self, time: int):
        if self.cfg['ROOT_POSITION_UPDATE_TYPE'] == 'velocity':
            fwd_vel = np.sum(self.bvh_fwd_vel[self.last_transferred_frame:time]) * self.motion_scaling_factor
            vrt_vel = np.sum(self.bvh_vrt_vel[self.last_transferred_frame:time]) * self.motion_scaling_factor
            self.sketch_root.local_matrix[0, -1] += fwd_vel
            self.sketch_root.local_matrix[1, -1] += vrt_vel
        elif self.cfg['ROOT_POSITION_UPDATE_TYPE'] == 'position':
            self.sketch_root.local_matrix[0, -1] = self.sketch_positions[time, 0]
            self.sketch_root.local_matrix[1, -1] = self.sketch_positions[time, 1]
        else:
            raise Exception('bad value for ROOT_POSITION_UPDATE_TYPE')
        self.last_transferred_frame = time
