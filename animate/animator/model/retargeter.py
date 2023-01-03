import logging
from animator.model.bvh import BVH
import numpy as np
import math
from animator.model.joint import Joint
from sklearn.decomposition import PCA

x_axis = np.array([1.0, 0.0, 0.0])
z_axis = np.array([0.0, 0.0, 1.0])


class Retargeter():

    def __init__(self, bvh_fn: str, bvh_projection_mapping: list):
        """
        bvh_fn: path to bvh file containing animation data
        bvh_projection_mapping: list of dicts containing groupings of joints, plane projection method, and grouping name
        """
        self.bvh = BVH.from_file(bvh_fn)
        self.joint_names = self.bvh.get_joint_names()

        self.joint_positions = self._compute_normalized_joint_positions()

        # get & save projection planes
        self.joint_to_projection_plane: dict = {}
        for joint_projection_group in bvh_projection_mapping:
            projection_plane = self._determine_projection_plane_normal(joint_projection_group)

            for joint_name in joint_projection_group['joint_names']:
                self.joint_to_projection_plane[joint_name] = projection_plane

        # used by compute_orientations() and get_orientations()
        self.char_joint_to_orientation: dict = {}

    def _compute_normalized_joint_positions(self) -> np.ndarray:
        """
        Extracts all joint world locations for all frames from self.bvh.
        Repositions them so each frame has root joint over origin.
        Rotates skeleton so each frame has skeleton facing towards world +X axis.
        Called during initialization.
        """
        # get joint positions and forward vectors for each frame in bvh
        joint_positions, fwd_vectors = self.bvh.get_all_joint_world_positions()

        # reposition over origin
        root_positions = np.tile(joint_positions[:, :3], [1, joint_positions.shape[1]//3])
        joint_positions = joint_positions - root_positions

        # rotate skeleton so it faces +X axis
        for idx in range(joint_positions.shape[0]):
            xa = np.array([1, 0])
            fv = fwd_vectors[idx]

            dot = fv[0]*xa[0] + fv[1]*xa[1]
            det = fv[0]*xa[1] - xa[0]*fv[1]
            angle = math.atan2(det, dot)

            rot_max = np.identity(3)
            rot_max[0, 0] = math.cos(angle)
            rot_max[0, 2] = math.sin(angle)
            rot_max[2, 0] = -math.sin(angle)
            rot_max[2, 2] = math.cos(angle)

            for jdx in range(joint_positions.shape[1]//3):
                v = joint_positions[idx, 3*jdx:3*jdx+3]
                v_prime = rot_max @ v
                joint_positions[idx, 3*jdx:3*jdx+3] = v_prime

        return joint_positions

    def _determine_projection_plane_normal(self, joint_projection_group: dict) -> np.ndarray:
        """
        Given a joint_projection_group dictionary object, computes the projection plane normal used for the group.
        Called during initialization.
        """

        if joint_projection_group['projection_method'] == 'frontal':
            return x_axis
        elif joint_projection_group['projection_method'] == 'saggital':
            return z_axis
        elif joint_projection_group['projection_method'] == 'pca':
            pass  # pca code is below
        else:
            msg = f'bad project method for {joint_projection_group["name"]}: {joint_projection_group["projection_method"]}'
            logging.critical(msg)
            assert False, msg

        # get the xyz locations of joints within this joint_projection_group
        joints_idxs = [self.joint_names.index(joint_name) for joint_name in joint_projection_group['joint_names']]
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
            return x_axis
        else:
            return z_axis

    def compute_orientations(self, bvh_prox_joint_name: str, bvh_dist_joint_name: str, char_joint_name: str) -> None:
        """
        Calculates the orientation (degrees CCW of +Y axis) of the vector from bvh_prox_joint->bvh_dist_joint using the
        projection plane of bvh_dist_joint. Results are saved into a dictionary using char_joint_name as the key.
        """

        # get distimal end joint
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
        dist_joint_idx = self.joint_names.index(dist_joint.name)
        dist_joint_xyz = self.joint_positions[:, 3*dist_joint_idx:3*(dist_joint_idx+1)]

        prox_joint_idx = self.joint_names.index(prox_joint.name)
        prox_joint_xyz = self.joint_positions[:, 3*prox_joint_idx:3*(prox_joint_idx+1)]

        # compute the bone vector
        bone_vector = dist_joint_xyz - prox_joint_xyz  # type: ignore

        # get projection plane
        try:
            projection_plane_normal = self.joint_to_projection_plane[bvh_dist_joint_name]
        except Exception:
            msg = f' error finding projection plane for bvh_end_joint_name: {bvh_dist_joint_name}'
            logging.critical(msg)
            assert False, msg

        # project bone onto 2D plane
        if np.array_equal(projection_plane_normal, x_axis):
            projected_bone_xy = np.stack((bone_vector[:, 2], bone_vector[:, 1]), axis=1)
        else:  # z axis
            projected_bone_xy = np.stack((bone_vector[:, 0], bone_vector[:, 1]), axis=1)

        # get angles between y axis and bone
        projected_bone_xy /= np.expand_dims(np.linalg.norm(projected_bone_xy, axis=1), axis=-1)  # norm vector
        y_axis = np.tile(np.array([0.0, 1.0]), reps=(projected_bone_xy.shape[0], 1))

        # compute theta, degrees CCW from +Y axis
        at1 = np.arctan2(projected_bone_xy[:, 1], projected_bone_xy[:, 0])
        at2 = np.arctan2(y_axis[:, 1], y_axis[:, 0])
        theta = at1 - at2  # type: ignore
        theta = np.degrees(theta) % 360
        theta = np.where(theta < 0.0, theta + 360, theta)

        # save it
        self.char_joint_to_orientation[char_joint_name] = theta

    def get_orientations(self, time: float) -> dict:
        """
        Given an input time, in seconds, compute the correct bvh frame to use.
        For that frame, creates a dictionary mapping from character joint names to world orienations (degrees CCW from +Y axis).
        """
        frame_idx = int(round(time / self.bvh.frame_time, 0))

        if not (0 < frame_idx < self.bvh.frame_max_num):
            msg = f'invalid frame_idx: {frame_idx}'
            logging.critical(msg)
            assert False, msg

        return {key: val[frame_idx] for (key, val) in self.char_joint_to_orientation.items()}
