import logging
from animator.model.bvh import BVH
import numpy as np
import math
from animator.model.joint import Joint
from sklearn.decomposition import PCA
from typing import Optional, Tuple, List
from animator.model.vectors import Vectors
from animator.model.quaternions import Quaternions
from pathlib import Path
import os

x_axis = np.array([1.0, 0.0, 0.0])
z_axis = np.array([0.0, 0.0, 1.0])


class Retargeter():

    def __init__(self, bvh_metadata_cfg: dict, char_bvh_retargeting_cfg: dict):
        """
        bvh_fn: path to bvh file containing animation data
        bvh_metadata_cfg: bvh metadata config dictionary
        """

        # Look for specified bvh file. First check using path specified, then relative to AD_ROOT_DIR. Abort if not found.
        if Path(bvh_metadata_cfg['filepath']).exists():
            bvh_fn: str = bvh_metadata_cfg['filepath']
        elif Path(os.environ['AD_ROOT_DIR'], bvh_metadata_cfg['filepath']):
            bvh_fn: str = str(Path(os.environ['AD_ROOT_DIR'], bvh_metadata_cfg['filepath']))
        else:
            msg = f'Could not find bvh file, aborting: {bvh_metadata_cfg["filepath"]}'
            logging.critical(msg)
            assert False, msg
        logging.info(f'Using bvh file: {bvh_fn}')

        # read start and end frame from config
        start_frame_idx = bvh_metadata_cfg.get('start_frame_idx', 0)
        end_frame_idx = bvh_metadata_cfg.get('end_frame_idx', None)

        # instantiate the bvh
        try:
            self.bvh = BVH.from_file(bvh_fn, start_frame_idx, end_frame_idx)
        except Exception as e:
            msg = f'Error loading BVH: {e}'
            logging.critical(msg)
            assert False, msg

        # get and cache bvh joint names for later
        self.bvh_joint_names = self.bvh.get_joint_names()

        # bvh joints defining a set of vectors that skeleton's fwd is perpendicular to
        self.forward_perp_vector_joint_names = bvh_metadata_cfg['forward_perp_joint_vectors']

        # rotate BVH skeleton so up is +Y
        if bvh_metadata_cfg['up'] == '+z':
            self.bvh.set_rotation(Quaternions.from_euler_angles('yx', np.array([-90.0, -90.0])))
        else:
            msg = f'bvh_metadata_cfg["up"] value not implemented: {bvh_metadata_cfg["up"]}'
            logging.warning(msg)

        # rotate BVH skeleton so forward is +X
        skeleton_fwd: Vectors = self.bvh.get_skeleton_fwd(self.forward_perp_vector_joint_names)
        q: Quaternions = Quaternions.rotate_between_vectors(skeleton_fwd, Vectors([1.0, 0.0, 0.0]))
        self.bvh.rotation_offset(q)

        # scale BVH
        try:
            self.bvh.set_scale(bvh_metadata_cfg['scale'])
        except Exception as e:
            msg = f'Could not scale BVH: {e}'
            logging.warning(msg)

        # position above origin
        self.bvh.offset(-self.bvh.root_joint.get_world_position())

        # adjust bvh skeleton height
        try:
            groundplane_joint = self.bvh.root_joint.get_joint_by_name(bvh_metadata_cfg['groundplane_joint'])
            if groundplane_joint is None:
                raise Exception(f'could not find groundplane_joint{bvh_metadata_cfg["groundplane_joint"]}')
            bvh_groundplane_y = groundplane_joint.get_world_position()[1]
            self.bvh.offset(np.array([0, -bvh_groundplane_y, 0]))  # reposition groundplane
        except Exception as e:
            msg = f'Could not use groundplane_joint to adjust bvh heightError getting groundplane joint: {str(e)}'
            logging.warning(msg)
            assert False

        self.joint_positions: np.ndarray
        self.fwd_vectors: np.ndarray
        self.bvh_root_positions: np.ndarray
        self._compute_normalized_joint_positions_and_fwd_vectors()

        # cache the starting worldspace location of character's root joint
        self.character_start_loc = np.array(char_bvh_retargeting_cfg['char_starting_location'])

        # holds world coordinates of character root joint after retargeting
        self.char_root_positions: Optional[np.ndarray] = None

        # get & save projection planes
        self.joint_group_name_to_projection_plane: dict = {}
        self.joint_to_projection_plane: dict = {}
        for joint_projection_group in char_bvh_retargeting_cfg['bvh_projection_bodypart_groups']:
            group_name = joint_projection_group['name']
            joint_names = joint_projection_group['bvh_joint_names']
            projection_method: str = joint_projection_group['method']

            projection_plane = self._determine_projection_plane_normal(group_name, joint_names, projection_method)
            self.joint_group_name_to_projection_plane[joint_projection_group['name']] = projection_plane

            for joint_name in joint_projection_group['bvh_joint_names']:
                self.joint_to_projection_plane[joint_name] = projection_plane

        # map character joint names to its orientations
        self.char_joint_to_orientation: dict = {}

        # map bvh joint names to its distance to project plane (useful for rendering order)
        self.bvh_joint_to_projection_depth: dict = self._compute_depths()

    def _compute_normalized_joint_positions_and_fwd_vectors(self) -> None:
        """
        Called during initialization.
        Computes fwd vector for bvh skeleton at each frame.
        Extracts all bvh skeleton joint locations for all frames.
        Repositions them so root is above the orign.
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

        # compute angle between skelton's forward vector and x axis
        v1 = np.tile(np.array([1.0, 0.0]), reps=(self.joint_positions.shape[0], 1))
        v2 = self.fwd_vectors
        dot = v1[:, 0]*v2[:, 0] + v1[:, 1]*v2[:, 2]
        det = v1[:, 0]*v2[:, 2] - v2[:, 0]*v1[:, 1]
        angle = np.arctan2(det, dot)
        angle %= 2*np.pi
        angle = np.where(angle < 0.0, angle + 2*np.pi, angle)

        # rotate the skeleton's joint so it faces +X axis
        for idx in range(self.joint_positions.shape[0]):
            rot_mat = np.identity(3)
            rot_mat[0, 0] = math.cos(angle[idx])
            rot_mat[0, 2] = math.sin(angle[idx])
            rot_mat[2, 0] = -math.sin(angle[idx])
            rot_mat[2, 2] = math.cos(angle[idx])

            rotated_joints = rot_mat @ self.joint_positions[idx].reshape([-1, 3]).T
            self.joint_positions[idx] = rotated_joints.T.reshape(self.joint_positions[idx].shape)

    def _determine_projection_plane_normal(self, group_name: str, joint_names: List[str], projection_method: str) -> np.ndarray:
        """
        Given a joint_projection_group dictionary object, computes the projection plane normal used for the group.
        Called during initialization.
        """

        if projection_method == 'frontal':
            logging.info(f'{group_name} projection_method is {projection_method}. Using {x_axis}')
            return x_axis
        elif projection_method == 'saggital':
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
        pc3 = pca.components_[2]  # type: ignore

        # see if it is closer to the x axis or z axis
        x_cos_sim = np.dot(x_axis, pc3) / (np.linalg.norm(x_axis) * np.linalg.norm(pc3))
        z_cos_sim = np.dot(z_axis, pc3) / (np.linalg.norm(z_axis) * np.linalg.norm(pc3))

        # return close of the two
        if abs(x_cos_sim) > abs(z_cos_sim):
            logging.info(f'PCA complete. {group_name} using {x_axis}')
            return x_axis
        else:
            logging.info(f'PCA complete. {group_name} using {z_axis}')
            return z_axis

    def _compute_depths(self) -> dict:
        """
        For each BVH joint within bvh_projection_mapping_groups, compute distance to projection plane.
        This distance used if the joint is a char_body_segmentation_groups depth_driver.
        """

        bvh_joint_to_projection_depth = {}

        for joint_name in self.bvh_joint_names:
            joint = self.bvh.root_joint.get_joint_by_name(joint_name)

            assert joint is not None
            assert self.joint_positions is not None

            joint_idx = self.bvh_joint_names.index(joint.name)
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

        self.char_root_positions = np.empty([self.bvh_root_positions.shape[0], 2])
        self.char_root_positions[0] = [0, 0]
        for idx in range(1, self.bvh_root_positions.shape[0]):

            if np.array_equal(projection_plane, np.array([0.0, 0.0, 1.0])):  # if saggital projection
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
        dist_joint = self.bvh.root_joint.get_joint_by_name(bvh_dist_joint_name)
        if dist_joint is None:
            msg = 'error finding joint {bvh_dist_joint_name}'
            logging.critical(msg)
            assert False, msg

        # get prox joint
        prox_joint = self.bvh.root_joint.get_joint_by_name(bvh_prox_joint_name)
        if prox_joint is None or not isinstance(prox_joint, Joint):
            msg = 'joint {bvh_prox_joint_name} has no parent joint, therefore no bone orientation. Returning zero'
            logging.info(msg)
            self.char_joint_to_orientation[char_joint_name] = np.zeros(self.joint_positions.shape[0])
            return

        # get joint xyz locations
        if not isinstance(self.joint_positions, np.ndarray):
            msg = 'joint_positions not initialized'
            logging.critical(msg)
            assert False, msg

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

        at1 = np.arctan2(projected_bone_xy[:, 1], projected_bone_xy[:, 0])
        at2 = np.arctan2(y_axis[:, 1], y_axis[:, 0])
        theta = at1 - at2  # type: ignore
        theta = np.degrees(theta) % 360
        theta = np.where(theta < 0.0, theta + 360, theta)

        # save it
        self.char_joint_to_orientation[char_joint_name] = np.array(theta)

    def get_retargeted_frame_data(self, time: float) -> Tuple[dict, dict, np.ndarray]:
        """
        Input: time, in seconds, used to select the correct BVH frame.
        Caculate the proper frame and, for it, returns:
            - orientations, dictionary mapping from character joint names to world orientations (degrees CCW from +Y axis)
            - joint_depths, dictionary mapping from BVH skeleton's joint names to distance from joint to projection plane
            - root_positions, the position of the character's root at this frame.
        """
        frame_idx = int(round(time / self.bvh.frame_time, 0))

        if frame_idx < 0:
            msg = f'invalid frame_idx, first frame (0) instead: {frame_idx}'
            logging.info(msg)
            frame_idx = 0

        if self.bvh.frame_max_num <= frame_idx:
            msg = f'invalid frame_idx, last frame ({self.bvh.frame_max_num-1}) instead: {frame_idx}'
            logging.info(msg)
            frame_idx = self.bvh.frame_max_num-1

        if self.char_root_positions is None:
            msg = 'self.char_root_positions not initialized.'
            logging.critical(msg)
            assert False, msg

        orientations = {key: val[frame_idx] for (key, val) in self.char_joint_to_orientation.items()}

        joint_depths = {key: val[frame_idx] for (key, val) in self.bvh_joint_to_projection_depth.items()}

        root_position = np.array([self.char_root_positions[frame_idx, 0], self.char_root_positions[frame_idx, 1], 0.0])
        root_position += self.character_start_loc  # offset by character's starting location

        return orientations, joint_depths, root_position
