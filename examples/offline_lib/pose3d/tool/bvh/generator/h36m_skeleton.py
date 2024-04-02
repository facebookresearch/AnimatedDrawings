from . import math3d
from . import bvh_helper

import numpy as np


class H36mSkeleton(object):

    def __init__(self):
        self.root = 'Hip'
        self.keypoint2index = {
            'Hip': 0,
            'RightHip': 1,
            'RightKnee': 2,
            'RightAnkle': 3,
            'LeftHip': 4,
            'LeftKnee': 5,
            'LeftAnkle': 6,
            'Spine': 7,
            'Thorax': 8,
            'Neck': 9,
            'HeadEndSite': 10,
            'LeftShoulder': 11,
            'LeftElbow': 12,
            'LeftWrist': 13,
            'RightShoulder': 14,
            'RightElbow': 15,
            'RightWrist': 16,
            'RightAnkleEndSite': -1,
            'LeftAnkleEndSite': -1,
            'LeftWristEndSite': -1,
            'RightWristEndSite': -1
        }

        self.index2keypoint = {v: k for k, v in self.keypoint2index.items()}
        self.keypoint_num = len(self.keypoint2index)

        self.children = {
            'Hip': ['RightHip', 'LeftHip', 'Spine'],
            'RightHip': ['RightKnee'],
            'RightKnee': ['RightAnkle'],
            'RightAnkle': ['RightAnkleEndSite'],
            'RightAnkleEndSite': [],
            'LeftHip': ['LeftKnee'],
            'LeftKnee': ['LeftAnkle'],
            'LeftAnkle': ['LeftAnkleEndSite'],
            'LeftAnkleEndSite': [],
            'Spine': ['Thorax'],
            'Thorax': ['Neck', 'LeftShoulder', 'RightShoulder'],
            'Neck': ['HeadEndSite'],
            'HeadEndSite': [], # Head is an end site
            'LeftShoulder': ['LeftElbow'],
            'LeftElbow': ['LeftWrist'],
            'LeftWrist': ['LeftWristEndSite'],
            'LeftWristEndSite': [],
            'RightShoulder': ['RightElbow'],
            'RightElbow': ['RightWrist'],
            'RightWrist': ['RightWristEndSite'],
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

        # human3.6m坐标系(Z向上，Y向前，X向左)下的T-pose
        self.initial_directions = {
            'Hip': [0, 0, 0],
            'RightHip': [-1, 0, 0],
            'RightKnee': [0, 0, -1],
            'RightAnkle': [0, 0, -1],
            'RightAnkleEndSite': [0, -1, 0],
            'LeftHip': [1, 0, 0],
            'LeftKnee': [0, 0, -1],
            'LeftAnkle': [0, 0, -1],
            'LeftAnkleEndSite': [0, -1, 0],
            'Spine': [0, 0, 1],
            'Thorax': [0, 0, 1],
            'Neck': [0, 0, 1],
            'HeadEndSite': [0, 0, 1],
            'LeftShoulder': [1, 0, 0],
            'LeftElbow': [1, 0, 0],
            'LeftWrist': [1, 0, 0],
            'LeftWristEndSite': [1, 0, 0],
            'RightShoulder': [-1, 0, 0],
            'RightElbow': [-1, 0, 0],
            'RightWrist': [-1, 0, 0],
            'RightWristEndSite': [-1, 0, 0]
        }

        # SmartBody坐标系(Y向上，Z向前，X向右)下的T-pose
        # self.initial_directions = {
        #     'Hip': [0, 0, 0],
        #     'RightHip': [-1, 0, 0],
        #     'RightKnee': [0, -1, 0],
        #     'RightAnkle': [0, -1, 0],
        #     'RightAnkleEndSite': [0, 0, -1],
        #     'LeftHip': [1, 0, 0],
        #     'LeftKnee': [0, -1, 0],
        #     'LeftAnkle': [0, -1, 0],
        #     'LeftAnkleEndSite': [0, 0, -1],
        #     'Spine': [0, 1, 0],
        #     'Thorax': [0, 1, 0],
        #     'Neck': [0, 1, 0],
        #     'HeadEndSite': [0, 1, 0],
        #     'LeftShoulder': [1, 0, 0],
        #     'LeftElbow': [1, 0, 0],
        #     'LeftWrist': [1, 0, 0],
        #     'LeftWristEndSite': [1, 0, 0],
        #     'RightShoulder': [-1, 0, 0],
        #     'RightElbow': [-1, 0, 0],
        #     'RightWrist': [-1, 0, 0],
        #     'RightWristEndSite': [-1, 0, 0]
        # }

        # self.initial_directions = {
        #     'Hips': [0, 0, 0],
        #     'RightUpLeg': [-1, 0, 0],
        #     'RightLeg': [0, -1, 0],
        #     'RightFoot': [0, -1, 0],
        #     'RightFoot_End': [0, 0, 1],
        #     'LeftUpLeg': [1, 0, 0],
        #     'LeftLeg': [0, -1, 0],
        #     'LeftFoot': [0, -1, 0],
        #     'LeftFoot_End': [0, 0, 1],
        #     'Spine': [0, 1, 0],
        #     'Spine3': [0, 1, 0],
        #     'Neck': [0, 1, 0],
        #     'Head': [0, 1, 0],
        #     'LeftArm': [1, 0, 0],
        #     'LeftForeArm': [1, 0, 0],
        #     'LeftHand': [1, 0, 0],
        #     'LeftWristEndSite': [1, 0, 0],
        #     'RightArm': [-1, 0, 0],
        #     'RightForeArm': [-1, 0, 0],
        #     'RightHand': [-1, 0, 0],
        #     'RightWristEndSite': [-1, 0, 0]
        # }

    def get_initial_offset(self, poses_3d):
        # TODO: RANSAC
        bone_lens = {self.root: [0]}
        stack = [self.root]
        while stack:
            parent = stack.pop()
            p_idx = self.keypoint2index[parent]
            for child in self.children[parent]:
                if 'EndSite' in child:
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

        return initial_offset


    def get_bvh_header(self, poses_3d):
        initial_offset = self.get_initial_offset(poses_3d)

        nodes = {}
        for joint in self.keypoint2index:
            is_root = joint == self.root
            is_end_site = 'EndSite' in joint
            nodes[joint] = bvh_helper.BvhNode(
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

        header = bvh_helper.BvhHeader(root=nodes[self.root], nodes=nodes)
        return header


    def pose2euler(self, pose, header):
        channel = []
        quats = {}
        eulers = {}
        stack = [header.root]
        while stack:
            node = stack.pop()
            joint = node.name
            # 得到关键点名称对应的索引下标
            joint_idx = self.keypoint2index[joint]
            
            if node.is_root:
                channel.extend(pose[joint_idx])

            index = self.keypoint2index
            order = None
            if joint == 'Hip':
                x_dir = pose[index['LeftHip']] - pose[index['RightHip']]
                y_dir = None
                z_dir = pose[index['Spine']] - pose[joint_idx]
                order = 'zyx'
            elif joint in ['RightHip', 'RightKnee']:
                child_idx = self.keypoint2index[node.children[0].name]
                x_dir = pose[index['Hip']] - pose[index['RightHip']]
                y_dir = None
                z_dir = pose[joint_idx] - pose[child_idx]
                order = 'zyx'
            elif joint in ['LeftHip', 'LeftKnee']:
                child_idx = self.keypoint2index[node.children[0].name]
                x_dir = pose[index['LeftHip']] - pose[index['Hip']]
                y_dir = None
                z_dir = pose[joint_idx] - pose[child_idx]
                order = 'zyx'
            elif joint == 'Spine':
                x_dir = pose[index['LeftHip']] - pose[index['RightHip']]
                y_dir = None
                z_dir = pose[index['Thorax']] - pose[joint_idx]
                order = 'zyx'
            elif joint == 'Thorax':
                x_dir = pose[index['LeftShoulder']] - \
                    pose[index['RightShoulder']]
                y_dir = None
                z_dir = pose[joint_idx] - pose[index['Spine']]
                order = 'zyx'
            elif joint == 'Neck':
                x_dir = None
                y_dir = pose[index['Thorax']] - pose[joint_idx]
                z_dir = pose[index['HeadEndSite']] - pose[index['Thorax']]
                order = 'zxy'
            elif joint == 'LeftShoulder':
                x_dir = pose[index['LeftElbow']] - pose[joint_idx]
                y_dir = pose[index['LeftElbow']] - pose[index['LeftWrist']]
                z_dir = None
                order = 'xzy'
            elif joint == 'LeftElbow':
                x_dir = pose[index['LeftWrist']] - pose[joint_idx]
                y_dir = pose[joint_idx] - pose[index['LeftShoulder']]
                z_dir = None
                order = 'xzy'
            elif joint == 'RightShoulder':
                x_dir = pose[joint_idx] - pose[index['RightElbow']]
                y_dir = pose[index['RightElbow']] - pose[index['RightWrist']]
                z_dir = None
                order = 'xzy'
            elif joint == 'RightElbow':
                x_dir = pose[joint_idx] - pose[index['RightWrist']]
                y_dir = pose[joint_idx] - pose[index['RightShoulder']]
                z_dir = None
                order = 'xzy'
            if order:
                dcm = math3d.dcm_from_axis(x_dir, y_dir, z_dir, order)
                quats[joint] = math3d.dcm2quat(dcm)
            else:
                quats[joint] = quats[self.parent[joint]].copy()
            
            local_quat = quats[joint].copy()
            if node.parent:
                local_quat = math3d.quat_divide(
                    q=quats[joint], r=quats[node.parent.name]
                )
            
            euler = math3d.quat2euler(
                q=local_quat, order=node.rotation_order
            )
            euler = np.rad2deg(euler)
            eulers[joint] = euler
            # 最后存入的是对应点欧拉的旋转角
            channel.extend(euler)

            for child in node.children[::-1]:
                if not child.is_end_site:
                    stack.append(child)

        return channel

    def pose2euler_SmartBody(self, pose, header):
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
            if joint == 'Hip':
                x_dir = pose[index['LeftHip']] - pose[index['RightHip']]
                z_dir = None
                y_dir = pose[index['Spine']] - pose[joint_idx]
                order = 'yzx'
            elif joint in ['RightHip', 'RightKnee']:
                child_idx = self.keypoint2index[node.children[0].name]
                x_dir = pose[index['Hip']] - pose[index['RightHip']]
                z_dir = None
                y_dir = pose[joint_idx] - pose[child_idx]
                order = 'yzx'
            elif joint in ['LeftHip', 'LeftKnee']:
                child_idx = self.keypoint2index[node.children[0].name]
                x_dir = pose[index['LeftHip']] - pose[index['Hip']]
                z_dir = None
                y_dir = pose[joint_idx] - pose[child_idx]
                order = 'yzx'
            elif joint == 'Spine':
                x_dir = pose[index['LeftHip']] - pose[index['RightHip']]
                z_dir = None
                y_dir = pose[index['Thorax']] - pose[joint_idx]
                order = 'yzx'
            elif joint == 'Thorax':
                x_dir = pose[index['LeftShoulder']] - \
                        pose[index['RightShoulder']]
                z_dir = None
                y_dir = pose[joint_idx] - pose[index['Spine']]
                order = 'yzx'
            elif joint == 'Neck':
                x_dir = None
                z_dir = pose[index['Thorax']] - pose[joint_idx]
                y_dir = pose[index['HeadEndSite']] - pose[index['Thorax']]
                order = 'yxz'
            elif joint == 'LeftShoulder':
                x_dir = pose[index['LeftElbow']] - pose[joint_idx]
                z_dir = pose[index['LeftElbow']] - pose[index['LeftWrist']]
                y_dir = None
                order = 'xyz'
            elif joint == 'LeftElbow':
                x_dir = pose[index['LeftWrist']] - pose[joint_idx]
                z_dir = pose[joint_idx] - pose[index['LeftShoulder']]
                y_dir = None
                order = 'xyz'
            elif joint == 'RightShoulder':
                x_dir = pose[joint_idx] - pose[index['RightElbow']]
                z_dir = pose[index['RightElbow']] - pose[index['RightWrist']]
                y_dir = None
                order = 'xyz'
            elif joint == 'RightElbow':
                x_dir = pose[joint_idx] - pose[index['RightWrist']]
                z_dir = pose[joint_idx] - pose[index['RightShoulder']]
                y_dir = None
                order = 'xyz'
            if order:
                dcm = math3d.dcm_from_axis(x_dir, y_dir, z_dir, order)
                quats[joint] = math3d.dcm2quat(dcm)
            else:
                quats[joint] = quats[self.parent[joint]].copy()

            local_quat = quats[joint].copy()
            if node.parent:
                local_quat = math3d.quat_divide(
                    q=quats[joint], r=quats[node.parent.name]
                )

            euler = math3d.quat2euler(
                q=local_quat, order=node.rotation_order
            )
            euler = np.rad2deg(euler)
            eulers[joint] = euler
            channel.extend(euler)

            for child in node.children[::-1]:
                if not child.is_end_site:
                    stack.append(child)

        return channel

    def pose2euler_SmartBody_Modify(self, pose, header):
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
                z_dir = None
                y_dir = pose[index['Spine']] - pose[joint_idx]
                order = 'yzx'
            elif joint in ['LeftUpLeg', 'RightLeg']:
                child_idx = self.keypoint2index[node.children[0].name]
                x_dir = pose[index['Hips']] - pose[index['RightUpLeg']]
                z_dir = None
                y_dir = pose[joint_idx] - pose[child_idx]
                order = 'yzx'
            elif joint in ['LeftUpLeg', 'LeftLeg']:
                child_idx = self.keypoint2index[node.children[0].name]
                x_dir = pose[index['LeftUpLeg']] - pose[index['Hips']]
                z_dir = None
                y_dir = pose[joint_idx] - pose[child_idx]
                order = 'yzx'
            elif joint == 'Spine':
                x_dir = pose[index['LeftUpLeg']] - pose[index['RightUpLeg']]
                z_dir = None
                y_dir = pose[index['Spine3']] - pose[joint_idx]
                order = 'yzx'
            elif joint == 'Spine3':
                x_dir = pose[index['LeftArm']] - \
                        pose[index['RightArm']]
                z_dir = None
                y_dir = pose[joint_idx] - pose[index['Spine']]
                order = 'yzx'
            elif joint == 'Neck':
                x_dir = None
                z_dir = pose[index['Spine3']] - pose[joint_idx]
                y_dir = pose[index['Head']] - pose[index['Spine3']]
                order = 'yxz'
            elif joint == 'LeftArm':
                x_dir = pose[index['LeftForeArm']] - pose[joint_idx]
                z_dir = pose[index['LeftForeArm']] - pose[index['LeftHand']]
                y_dir = None
                order = 'xyz'
            elif joint == 'LeftForeArm':
                x_dir = pose[index['LeftHand']] - pose[joint_idx]
                z_dir = pose[joint_idx] - pose[index['LeftArm']]
                y_dir = None
                order = 'xyz'
            elif joint == 'RightArm':
                x_dir = pose[joint_idx] - pose[index['RightForeArm']]
                z_dir = pose[index['RightForeArm']] - pose[index['RightHand']]
                y_dir = None
                order = 'xyz'
            elif joint == 'RightForeArm':
                x_dir = pose[joint_idx] - pose[index['RightHand']]
                z_dir = pose[joint_idx] - pose[index['RightArm']]
                y_dir = None
                order = 'xyz'
            if order:
                dcm = math3d.dcm_from_axis(x_dir, y_dir, z_dir, order)
                quats[joint] = math3d.dcm2quat(dcm)
            else:
                quats[joint] = quats[self.parent[joint]].copy()

            local_quat = quats[joint].copy()
            if node.parent:
                local_quat = math3d.quat_divide(
                    q=quats[joint], r=quats[node.parent.name]
                )

            euler = math3d.quat2euler(
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
            #channels.append(self.pose2euler_SmartBody(pose, header))
            #channels.append(self.pose2euler_SmartBody_Modify(pose, header))

        if output_file:
            bvh_helper.write_bvh(output_file, header, channels)
        
        return channels, header