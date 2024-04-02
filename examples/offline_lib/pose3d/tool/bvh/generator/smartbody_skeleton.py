from . import math3d_SmartBody
from . import bvh_helper_SmartBody

import numpy as np


class SmartBodySkeleton(object):

    def __init__(self):
        self.root = 'Hips'
        self.keypoint2index = {
            'Hips': 0,
            'RightUpLeg': 1,
            'RightLeg': 2,
            'RightFoot': 3,
            'LeftUpLeg': 4,
            'LeftLeg': 5,
            'LeftFoot': 6,
            'Spine': 7,
            'Spine3': 8,
            'Neck': 9,
            'Head': 10,
            'LeftArm': 11,
            'LeftForeArm': 12,
            'LeftHand': 13,
            'RightArm': 14,
            'RightForeArm': 15,
            'RightHand': 16,
            'RightFoot_End': -1,
            'LeftFoot_End': -1,
            'LeftWristEndSite': -1,
            'RightWristEndSite': -1
        }

        self.root = 'Hips'
        self.keypoint2index = {
            'Hips': 0,
            'RightUpLeg': 1,
            'RightLeg': 2,
            'RightFoot': 3,
            'LeftUpLeg': 4,
            'LeftLeg': 5,
            'LeftFoot': 6,
            'Spine': 7,
            'Spine3': 8,
            'Neck': 9,
            'Head': 10,
            'LeftArm': 11,
            'LeftForeArm': 12,
            'LeftHand': 13,
            'RightArm': 14,
            'RightForeArm': 15,
            'RightHand': 16,
            'RightFoot_End': -1,
            'LeftFoot_End': -1,
            'LeftWristEndSite': -1,
            'RightWristEndSite': -1
        }

        self.index2keypoint = {v: k for k, v in self.keypoint2index.items()}
        self.keypoint_num = len(self.keypoint2index)

        self.children = {
            'Hips': ['RightUpLeg', 'LeftUpLeg', 'Spine'],
            'RightUpLeg': ['RightLeg'],
            'RightLeg': ['RightFoot'],
            'RightFoot': ['RightFoot_End'],
            'RightFoot_End': [],
            'LeftUpLeg': ['LeftLeg'],
            'LeftLeg': ['LeftFoot'],
            'LeftFoot': ['LeftFoot_End'],
            'LeftFoot_End': [],
            'Spine': ['Spine3'],
            'Spine3': ['Neck', 'LeftArm', 'RightArm'],
            'Neck': ['Head'],
            'Head': [],  # Head is an end site
            'LeftArm': ['LeftForeArm'],
            'LeftForeArm': ['LeftHand'],
            'LeftHand': ['LeftWristEndSite'],
            'LeftWristEndSite': [],
            'RightArm': ['RightForeArm'],
            'RightForeArm': ['RightHand'],
            'RightHand': ['RightWristEndSite'],
            'RightWristEndSite': []
        }

        self.parent = {self.root: None}
        for parent, children in self.children.items():
            for child in children:
                self.parent[child] = parent

        self.left_joints = [
            joint for joint in self.keypoint2index
            if 'Left' in joint
        ]
        self.right_joints = [
            joint for joint in self.keypoint2index
            if 'Right' in joint
        ]

        # SmartBody坐标系(Y向上，Z向前，X向右)下的T-pose
        self.initial_directions = {
            'Hips': [0, 0, 0],
            'RightUpLeg': [-1, 0, 0],
            'RightLeg': [0, -1, 0],
            'RightFoot': [0, -1, 0],
            'RightFoot_End': [0, 0, 1],
            'LeftUpLeg': [1, 0, 0],
            'LeftLeg': [0, -1, 0],
            'LeftFoot': [0, -1, 0],
            'LeftFoot_End': [0, 0, 1],
            'Spine': [0, 1, 0],
            'Spine3': [0, 1, 0],
            'Neck': [0, 1, 0],
            'Head': [0, 1, 0],
            'LeftArm': [1, 0, 0],
            'LeftForeArm': [1, 0, 0],
            'LeftHand': [1, 0, 0],
            'LeftWristEndSite': [1, 0, 0],
            'RightArm': [-1, 0, 0],
            'RightForeArm': [-1, 0, 0],
            'RightHand': [-1, 0, 0],
            'RightWristEndSite': [-1, 0, 0]
        }

    def get_initial_offset(self, poses_3d):
        # TODO: RANSAC
        bone_lens = {self.root: [0]}
        stack = [self.root]
        while stack:
            parent = stack.pop()
            p_idx = self.keypoint2index[parent]
            for child in self.children[parent]:
                if 'End' in child or child == 'Head':
                    bone_lens[child] = 0.4 * bone_lens[parent]
                    continue
                stack.append(child)

                c_idx = self.keypoint2index[child]
                bone_lens[child] = np.linalg.norm(
                    poses_3d[:, p_idx] - poses_3d[:, c_idx],
                    axis=1
                )

        bone_len = {}
        for joint in self.keypoint2index:
            if 'Left' in joint or 'Right' in joint:
                base_name = joint.replace('Left', '').replace('Right', '')
                left_len = np.mean(bone_lens['Left' + base_name])
                right_len = np.mean(bone_lens['Right' + base_name])
                bone_len[joint] = (left_len + right_len) / 2
            else:
                bone_len[joint] = np.mean(bone_lens[joint])

        initial_offset = {}
        for joint, direction in self.initial_directions.items():
            direction = np.array(direction) / max(np.linalg.norm(direction), 1e-12)
            initial_offset[joint] = direction * bone_len[joint]

        initial_offset['Hips'] = (initial_offset['RightFoot_End'] + initial_offset['RightFoot'] + initial_offset['RightLeg'] + initial_offset['RightUpLeg'] + initial_offset['Hips'])
        initial_offset['Hips'] *= -1

        return initial_offset

    def get_bvh_header(self, poses_3d):
        initial_offset = self.get_initial_offset(poses_3d)

        nodes = {}
        for joint in self.keypoint2index:
            is_root = joint == self.root
            # is_end_site = 'EndSite' in joint
            is_end_site = 'End' in joint or joint == 'Head'
            nodes[joint] = bvh_helper_SmartBody.BvhNode(
                name=joint,
                offset=initial_offset[joint],
                rotation_order='zxy' if not is_end_site else '',
                is_root=is_root,
                is_end_site=is_end_site,
            )
        for joint, children in self.children.items():
            nodes[joint].children = [nodes[child] for child in children]
            for child in children:
                nodes[child].parent = nodes[joint]

        header = bvh_helper_SmartBody.BvhHeader(root=nodes[self.root], nodes=nodes)
        return header

    def pose2euler(self, pose, header):
        channel = []
        quats = {}
        eulers = {}
        stack = [header.root]
        while stack:
            node = stack.pop()
            joint = node.name
            joint_idx = self.keypoint2index[joint]

            if node.is_root:
                channel.extend(pose[joint_idx])

            index = self.keypoint2index
            order = None
            if joint == 'Hips':
                x_dir = pose[index['LeftUpLeg']] - pose[index['RightUpLeg']]
                y_dir = pose[index['Spine']] - pose[joint_idx]
                z_dir = None
                order = 'yzx'
            elif joint in ['RightUpLeg', 'RightLeg']:
                child_idx = self.keypoint2index[node.children[0].name]
                x_dir = pose[index['Hips']] - pose[index['RightUpLeg']]
                y_dir = pose[joint_idx] - pose[child_idx]
                z_dir = None
                order = 'yzx'
            elif joint in ['LeftUpLeg', 'LeftLeg']:
                child_idx = self.keypoint2index[node.children[0].name]
                x_dir = pose[index['LeftUpLeg']] - pose[index['Hips']]
                y_dir = pose[joint_idx] - pose[child_idx]
                z_dir = None
                order = 'yzx'
            elif joint == 'Spine':
                x_dir = pose[index['LeftUpLeg']] - pose[index['RightUpLeg']]
                y_dir = pose[index['Spine3']] - pose[joint_idx]
                z_dir = None
                order = 'yzx'
            elif joint == 'Spine3':
                x_dir = pose[index['LeftArm']] - \
                        pose[index['RightArm']]
                y_dir = pose[joint_idx] - pose[index['Spine']]
                z_dir = None
                order = 'yzx'
            elif joint == 'Neck':
                x_dir = None
                z_dir = pose[index['Spine3']] - pose[joint_idx]
                y_dir = pose[index['Head']] - pose[index['Spine3']]
                order = 'yxz'
            elif joint == 'LeftArm':
                x_dir = pose[index['LeftForeArm']] - pose[joint_idx]
                y_dir = None
                z_dir = pose[index['LeftForeArm']] - pose[index['LeftHand']]
                order = 'xyz'

                # y_dir = pose[index['Neck']]-pose[index['Spine3']]
                # z_dir = None
                # order = 'xzy'

            elif joint == 'LeftForeArm':
                x_dir = pose[index['LeftHand']] - pose[joint_idx]
                y_dir = None
                z_dir = pose[joint_idx] - pose[index['LeftArm']]
                order = 'xyz'
            elif joint == 'RightArm':
                x_dir = pose[joint_idx] - pose[index['RightForeArm']]
                y_dir = None
                z_dir = pose[index['RightForeArm']] - pose[index['RightHand']]
                order = 'xyz'

                # y_dir = pose[index['Neck']]-pose[index['Spine3']]
                # z_dir = None
                # order = 'xzy'
            elif joint == 'RightForeArm':
                x_dir = pose[joint_idx] - pose[index['RightHand']]
                y_dir = None
                z_dir = pose[joint_idx] - pose[index['RightArm']]
                order = 'xyz'
            if order:
                dcm = math3d_SmartBody.dcm_from_axis(x_dir, y_dir, z_dir, order)
                quats[joint] = math3d_SmartBody.dcm2quat(dcm)
            else:
                quats[joint] = quats[self.parent[joint]].copy()

            local_quat = quats[joint].copy()
            if node.parent:
                local_quat = math3d_SmartBody.quat_divide(
                    q=quats[joint], r=quats[node.parent.name]
                )

            euler = math3d_SmartBody.quat2euler(
                q=local_quat, order=node.rotation_order
            )
            euler = np.rad2deg(euler)
            eulers[joint] = euler
            channel.extend(euler)

            for child in node.children[::-1]:
                if not child.is_end_site:
                    stack.append(child)

        return channel

    def poses2bvh(self, poses_3d, header=None, output_file=None):
        if not header:
            header = self.get_bvh_header(poses_3d)

        channels = []
        for frame, pose in enumerate(poses_3d):
            channels.append(self.pose2euler(pose, header))

        if output_file:
            bvh_helper_SmartBody.write_bvh(output_file, header, channels)

        return channels, header