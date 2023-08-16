# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import logging
from animated_drawings.model.bvh import BVH
import numpy as np
import numpy.typing as npt
import math
from animated_drawings.model.joint import Joint
from sklearn.decomposition import PCA
from typing import Tuple, List, Dict
from animated_drawings.model.vectors import Vectors
from animated_drawings.model.quaternions import Quaternions
from animated_drawings.config import MotionConfig, RetargetConfig

x_axis = np.array([1.0, 0.0, 0.0], dtype=np.float32)
z_axis = np.array([0.0, 0.0, 1.0], dtype=np.float32)


class Retargeter():
    """
    Retargeter class takes in a motion_cfg file and retarget_cfg file.
    Using the specifications listed within retarget_cfg, it converts the motion
    specified in motion_cfg into a formal that can be applied to an animated drawing.
    It is responsible for project 3D joint locations onto 2D planes, determining resulting
    bone orientations, joint 'depths', and root offsets for each frame.
    """

    def __init__(self, motion_cfg: MotionConfig, retarget_cfg: RetargetConfig) -> None:

        # instantiate the bvh
        try:
            self.bvh = BVH.from_file(str(motion_cfg.bvh_p), motion_cfg.start_frame_idx, motion_cfg.end_frame_idx)
        except Exception as e:
            msg = f'Error loading BVH: {e}'
            logging.critical(msg)
            assert False, msg

        # get and cache bvh joint names for later
        self.bvh_joint_names = self.bvh.get_joint_names()

        # bvh joints defining a set of vectors that skeleton's fwd is perpendicular to
        self.forward_perp_vector_joint_names: List[Tuple[str, str]] = motion_cfg.forward_perp_joint_vectors

        # override the frame_time, if one was specified within motion_cfg
        if motion_cfg.frame_time:
            self.bvh.frame_time = motion_cfg.frame_time

        # rotate BVH skeleton so up is +Y
        if motion_cfg.up == '+y':
            pass  # no rotation needed
        elif motion_cfg.up == '+z':
            self.bvh.set_rotation(Quaternions.from_euler_angles('yx', np.array([-90.0, -90.0])))
        else:
            msg = f'up value not implemented: {motion_cfg.up}'
            logging.critical(msg)
            assert False, msg

        # rotate BVH skeleton so forward is +X
        skeleton_fwd: Vectors = self.bvh.get_skeleton_fwd(self.forward_perp_vector_joint_names)
        q: Quaternions = Quaternions.rotate_between_vectors(skeleton_fwd, Vectors([1.0, 0.0, 0.0]))
        self.bvh.rotation_offset(q)

        # scale BVH
        self.bvh.set_scale(motion_cfg.scale)

        # position above origin
        self.bvh.offset(-self.bvh.root_joint.get_world_position())

        # adjust bvh skeleton y pos by getting groundplane joint...
        try:
            groundplane_joint = self.bvh.root_joint.get_transform_by_name(motion_cfg.groundplane_joint)
            assert isinstance(groundplane_joint, Joint), f'could not find joint by name: {motion_cfg.groundplane_joint}'
        except Exception as e:
            msg = f'Error getting groundplane joint: {e}'
            logging.warning(msg)
            assert False

        # ... and moving the bvh so it is on the y=0 plane
        bvh_groundplane_y = groundplane_joint.get_world_position()[1]
        self.bvh.offset(np.array([0, -bvh_groundplane_y, 0]))

        self.joint_positions: npt.NDArray[np.float32]
        self.fwd_vectors: npt.NDArray[np.float32]
        self.bvh_root_positions: npt.NDArray[np.float32]
        self._compute_normalized_joint_positions_and_fwd_vectors()

        # cache the starting worldspace location of character's root joint
        self.character_start_loc: npt.NDArray[np.float32] = np.array(retarget_cfg.char_start_loc, dtype=np.float32)

        # holds world coordinates of character root joint after retargeting
        self.char_root_positions: npt.NDArray[np.float32]

        # get & save projection planes
        self.joint_group_name_to_projection_plane: Dict[ str, npt.NDArray[np.float32]] = {}
        self.joint_to_projection_plane: Dict[ str, npt.NDArray[np.float32]] = {}
        for joint_projection_group in retarget_cfg.bvh_projection_bodypart_groups:
            group_name = joint_projection_group['name']
            joint_names = joint_projection_group['bvh_joint_names']
            projection_method = joint_projection_group['method']

            projection_plane = self._determine_projection_plane_normal(group_name, joint_names, projection_method)
            self.joint_group_name_to_projection_plane[joint_projection_group['name']] = projection_plane

            for joint_name in joint_projection_group['bvh_joint_names']:
                self.joint_to_projection_plane[joint_name] = projection_plane

        # map character joint names to its orientations
        self.char_joint_to_orientation: Dict[str, npt.NDArray[np.float32]] = {}

        # map bvh joint names to its distance to project plane (useful for rendering order)
        self.bvh_joint_to_projection_depth: Dict[str, npt.NDArray[np.float32]] = self._compute_depths()

    def _compute_normalized_joint_positions_and_fwd_vectors(self) -> None:
        """
        Called during initialization.
        Computes fwd vector for bvh skeleton at each frame.
        Extracts all bvh skeleton joint locations for all frames.
        Repositions them so root is above the origin.
        Rotates them so skeleton faces along the +X axis.
        """
        # get joint positions and forward vectors
        self.joint_positions = np.empty([self.bvh.frame_max_num, 3 * self.bvh.joint_num], dtype=np.float32)
        self.fwd_vectors = np.empty([self.bvh.frame_max_num, 3], dtype=np.float32)
        for frame_idx in range(self.bvh.frame_max_num):
            self.bvh.apply_frame(frame_idx)
            self.joint_positions[frame_idx] = self.bvh.root_joint.get_chain_worldspace_positions()
            self.fwd_vectors[frame_idx] = self.bvh.get_skeleton_fwd(self.forward_perp_vector_joint_names).vs[0]

        # reposition over origin
        self.bvh_root_positions = self.joint_positions[:, :3]
        self.joint_positions = self.joint_positions - np.tile(self.bvh_root_positions, [1, len(self.bvh_joint_names)])

        # compute angle between skeleton's forward vector and x axis
        v1 = np.tile(np.array([1.0, 0.0], dtype=np.float32), reps=(self.joint_positions.shape[0], 1))
        v2 = self.fwd_vectors
        dot: npt.NDArray[np.float32] = v1[:, 0]*v2[:, 0] + v1[:, 1]*v2[:, 2]
        det: npt.NDArray[np.float32] = v1[:, 0]*v2[:, 2] - v2[:, 0]*v1[:, 1]
        angle: npt.NDArray[np.float32] = np.arctan2(det, dot).astype(np.float32)
        angle %= 2*np.pi
        angle = np.where(angle < 0.0, angle + 2*np.pi, angle)

        # rotate the skeleton's joint so it faces +X axis
        for idx in range(self.joint_positions.shape[0]):
            rot_mat = np.identity(3).astype(np.float32)
            rot_mat[0, 0] = math.cos(angle[idx])
            rot_mat[0, 2] = math.sin(angle[idx])
            rot_mat[2, 0] = -math.sin(angle[idx])
            rot_mat[2, 2] = math.cos(angle[idx])

            rotated_joints: npt.NDArray[np.float32] = rot_mat @ self.joint_positions[idx].reshape([-1, 3]).T
            self.joint_positions[idx] = rotated_joints.T.reshape(self.joint_positions[idx].shape)

    def _determine_projection_plane_normal(self, group_name: str, joint_names: List[str], projection_method: str) -> npt.NDArray[np.float32]:
        """
        Given a joint_projection_group dictionary object, computes the projection plane normal used for the group.
        Called during initialization.
        """

        if projection_method == 'frontal':
            logging.info(f'{group_name} projection_method is {projection_method}. Using {x_axis}')
            return x_axis
        elif projection_method == 'sagittal':
            logging.info(f'{group_name} projection_method is {projection_method}. Using {z_axis}')
            return z_axis
        elif projection_method == 'pca':
            logging.info(f'{group_name} projection_method is {projection_method}. Running PCA on {joint_names}')
            pass  # pca code is below
        else:
            msg = f'bad project method for {group_name}: {projection_method}'
            logging.critical(msg)
            assert False, msg

        # get the xyz locations of joints within this joint_projection_group
        joints_idxs = [self.bvh_joint_names.index(joint_name) for joint_name in joint_names]
        joints_mask = np.full(self.joint_positions.shape[1], False, dtype=np.bool8)
        for idx in joints_idxs:
            joints_mask[3*idx:3*(idx+1)] = True
        joints_points = self.joint_positions[:, joints_mask]
        joints_points = joints_points.reshape([-1, 3])

        # do PCA and get 3rd component
        pca = PCA()
        pca.fit(joints_points)
        pc3: npt.NDArray[np.float32] = pca.components_[2]  # pyright: ignore[reportGeneralTypeIssues]

        # see if it is closer to the x axis or z axis
        x_cos_sim: float = np.dot(x_axis, pc3) / (np.linalg.norm(x_axis) * np.linalg.norm(pc3))
        z_cos_sim: float = np.dot(z_axis, pc3) / (np.linalg.norm(z_axis) * np.linalg.norm(pc3))

        # return close of the two
        if abs(x_cos_sim) > abs(z_cos_sim):
            logging.info(f'PCA complete. {group_name} using {x_axis}')
            return x_axis
        else:
            logging.info(f'PCA complete. {group_name} using {z_axis}')
            return z_axis

    def _compute_depths(self) -> Dict[str, npt.NDArray[np.float32]]:
        """
        For each BVH joint within bvh_projection_mapping_groups, compute distance to projection plane.
        This distance used if the joint is a char_body_segmentation_groups depth_driver.
        """

        bvh_joint_to_projection_depth: Dict[str, npt.NDArray[np.float32]] = {}

        for joint_name in self.bvh_joint_names:
            joint_idx = self.bvh_joint_names.index(joint_name)
            joint_xyz = self.joint_positions[:, 3*joint_idx:3*(joint_idx+1)]
            try:
                projection_plane_normal = self.joint_to_projection_plane[joint_name]
            except Exception:
                msg = f' error finding projection plane for joint_name: {joint_name}'
                logging.info(msg)
                continue

            # project bone onto 2D plane
            if np.array_equal(projection_plane_normal, x_axis):
                joint_depths = joint_xyz[:, 0]
            elif np.array_equal(projection_plane_normal, z_axis):
                joint_depths = joint_xyz[:, 2]
            else:
                msg = 'error projection_plane_normal'
                logging.critical(msg)
                assert False, msg
            bvh_joint_to_projection_depth[joint_name] = joint_depths

        return bvh_joint_to_projection_depth

    def scale_root_positions_for_character(self, char_to_bvh_scale: float, projection_bodypart_group_for_offset: str) -> None:
        """
        Uses projection plane of projection_bodypart_group_for_offset to determine bvh skeleton's projected root offset.
        Scales that offset to account for differences in lengths of character and bvh skeleton limbs.
        """
        try:
            projection_plane = self.joint_group_name_to_projection_plane[projection_bodypart_group_for_offset]
        except Exception as e:
            msg = f'Error getting projection plane: {str(e)}'
            logging.critical(msg)
            assert False, msg

        self.char_root_positions = np.empty([self.bvh_root_positions.shape[0], 2], dtype=np.float32)
        self.char_root_positions[0] = [0, 0]
        for idx in range(1, self.bvh_root_positions.shape[0]):

            if np.array_equal(projection_plane, np.array([0.0, 0.0, 1.0])):  # if sagittal projection
                v1 = self.fwd_vectors[idx]                                   # we're interested in forward motion
            else:                                                            # if frontal projection
                v1 = self.fwd_vectors[idx][::-1]*np.array([-1, 1, -1])       # we're interested in lateral motion

            delta = self.bvh_root_positions[idx] - self.bvh_root_positions[idx-1]

            # scale root delta for both x and y offsets. Project onto v1 for x offset
            self.char_root_positions[idx, 0] = self.char_root_positions[idx-1, 0] + char_to_bvh_scale * np.dot(v1, delta)  # x
            self.char_root_positions[idx, 1] = self.char_root_positions[idx-1, 1] + char_to_bvh_scale * delta[1]           # y

    def compute_orientations(self, bvh_prox_joint_name: str, bvh_dist_joint_name: str, char_joint_name: str) -> None:
        """
        Calculates the orientation (degrees CCW of +Y axis) of the vector from bvh_prox_joint->bvh_dist_joint using the
        projection plane of bvh_dist_joint. Results are saved into a dictionary using char_joint_name as the key.
        """

        # get distal end joint
        dist_joint = self.bvh.root_joint.get_transform_by_name(bvh_dist_joint_name)
        if dist_joint is None or not isinstance(dist_joint, Joint) or dist_joint.name is None:
            msg = 'error finding joint {bvh_dist_joint_name}'
            logging.critical(msg)
            assert False, msg

        # get prox joint
        prox_joint = self.bvh.root_joint.get_transform_by_name(bvh_prox_joint_name)
        if prox_joint is None or not isinstance(prox_joint, Joint) or prox_joint.name is None:
            msg = 'joint {bvh_prox_joint_name} has no parent joint, therefore no bone orientation. Returning zero'
            logging.info(msg)
            self.char_joint_to_orientation[char_joint_name] = np.zeros(self.joint_positions.shape[0], dtype=np.float32)
            return

        # get joint xyz locations
        dist_joint_idx = self.bvh_joint_names.index(dist_joint.name)
        dist_joint_xyz = self.joint_positions[:, 3*dist_joint_idx:3*(dist_joint_idx+1)]

        prox_joint_idx = self.bvh_joint_names.index(prox_joint.name)
        prox_joint_xyz = self.joint_positions[:, 3*prox_joint_idx:3*(prox_joint_idx+1)]

        # compute the bone vector
        bone_vector = dist_joint_xyz - prox_joint_xyz  # type: ignore

        # get distal joint's projection plane
        try:
            projection_plane_normal = self.joint_to_projection_plane[bvh_dist_joint_name]
        except Exception:
            msg = f' error finding projection plane for bvh_end_joint_name: {bvh_dist_joint_name}'
            logging.critical(msg)
            assert False, msg

        # project bone onto 2D plane
        if np.array_equal(projection_plane_normal, x_axis):
            projected_bone_xy = np.stack((-bone_vector[:, 2], bone_vector[:, 1]), axis=1)
        elif np.array_equal(projection_plane_normal, z_axis):
            projected_bone_xy = np.stack((bone_vector[:, 0], bone_vector[:, 1]), axis=1)
        else:
            msg = 'error projection_plane_normal'
            logging.critical(msg)
            assert False, msg

        # get angles between y axis and bone
        projected_bone_xy /= np.expand_dims(np.linalg.norm(projected_bone_xy, axis=1), axis=-1)  # norm vector
        y_axis = np.tile(np.array([0.0, 1.0]), reps=(projected_bone_xy.shape[0], 1))

        at1 = np.arctan2(projected_bone_xy[:, 1], projected_bone_xy[:, 0], dtype=np.float32)
        at2 = np.arctan2(y_axis[:, 1], y_axis[:, 0], dtype=np.float32)
        theta: npt.NDArray[np.float32]  = at1 - at2  # type: ignore
        theta = np.degrees(theta) % 360.0
        theta = np.where(theta < 0.0, theta + 360, theta)

        # save it
        self.char_joint_to_orientation[char_joint_name] = np.array(theta)

    def get_retargeted_frame_data(self, time: float) -> Tuple[Dict[str, float], Dict[str, float], npt.NDArray[np.float32]]:
        """
        Input: time, in seconds, used to select the correct BVH frame.
        Calculate the proper frame and, for it, returns:
            - orientations, dictionary mapping from character joint names to world orientations (degrees CCW from +Y axis)
            - joint_depths, dictionary mapping from BVH skeleton's joint names to distance from joint to projection plane
            - root_positions, the position of the character's root at this frame.
        """
        frame_idx = int(round(time / self.bvh.frame_time, 0))

        if frame_idx < 0:
            logging.info(f'invalid frame_idx ({frame_idx}), replacing with 0')
            frame_idx = 0

        if self.bvh.frame_max_num <= frame_idx:
            logging.info(f'invalid frame_idx ({frame_idx}), replacing with last frame {self.bvh.frame_max_num-1}')
            frame_idx = self.bvh.frame_max_num-1

        orientations = {key: val[frame_idx] for (key, val) in self.char_joint_to_orientation.items()}

        joint_depths = {key: val[frame_idx] for (key, val) in self.bvh_joint_to_projection_depth.items()}

        root_position = np.array([self.char_root_positions[frame_idx, 0], self.char_root_positions[frame_idx, 1], 0.0], dtype=np.float32)
        root_position += self.character_start_loc  # offset by character's starting location

        return orientations, joint_depths, root_position
