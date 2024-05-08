# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import annotations  # so we can refer to class Type inside class
import logging
from pathlib import Path
from typing import List, Tuple, Optional, Union, Dict

import numpy as np
import numpy.typing as npt

from .transform import Transform
# from .box import Box
from .quaternions import Quaternions
from .vectors import Vectors
from .joint import Joint
from .time_manager import TimeManager
from .utils import resolve_ad_filepath
from copy import deepcopy


class BVH_Joint(Joint):
    """
        Joint class with channel order attribute and specialized vis widget
    """

    def __init__(self, channel_order: List[str] = [], widget: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)

        self.channel_order = channel_order

        self.widget: Optional[Transform] = None

    def _draw(self, **kwargs):
        assert NotImplementedError


class BVH(Transform, TimeManager):
    """
    Class to encapsulate BVH (Biovision Hierarchy) animation data.
    Include a single skeletal hierarchy defined in the BVH, frame count and speed,
    and skeletal pos/rot data for each frame
    """

    # BVH结束标志
    END_JOINT_NAME: Tuple[str] = ("end site", "end_site", "End Site", "End_Site")

    def __init__(self,
                 name: str,
                 root_joint: BVH_Joint,
                 frame_max_num: int,
                 frame_time: float,
                 pos_data: npt.NDArray[np.float32],
                 rot_data: npt.NDArray[np.float32],
                 init_eular_rot_data: npt.NDArray[np.float32] = np.array([0., 0., 0.])
                 ) -> None:
        """
        Don't recommend calling this method directly.  Instead, use BVH.from_file().
        """
        super().__init__()

        self.name: str = name
        self.frame_max_num: int = frame_max_num
        self.frame_time: float = frame_time

        # 存储根节点的offset [T,C]
        self.pos_data: npt.NDArray[np.float32] = pos_data
        # 存储各个关节点的旋转角 [T,V,4] 用四元数表示
        self.rot_data: npt.NDArray[np.float32] = rot_data

        # BVH_Joint类型
        self.root_joint = root_joint
        self.add_child(self.root_joint)
        self.joint_num = self.root_joint.joint_count()

        # 从经过格式化后的所有节点中按照之前设定好的深度优先遍历顺序去存储每个节点相对于父结点(根结点的父节点为虚拟的世界坐标原点)的本地偏移量
        # From Parsed Skeleton to acquie init local offset [V,C=3]
        self.init_local_offset: npt.NDArray[np.float32] = np.stack(self.get_joints_init_local_offset(), axis=0)

        #########################################################################
        # 初始化各个旋转角应该都为0 [V,Q=4]
        root_axis_chars = "".join([c[0].lower() for c in self.root_joint.channel_order if c.endswith('rotation')])
        # excpet root joint, other joints have zero rotation, so the rotation orders have few effect
        zero_q: npt.NDArray[np.float32] = Quaternions.from_euler_angles(order=root_axis_chars,
                                                                        angles=np.array([0.0, 0.0, 0.0],
                                                                                        dtype=np.float32))
        root_zero_q = Quaternions.from_euler_angles(root_axis_chars, angles=init_eular_rot_data)

        #################################################################################
        self.init_rot_data: npt.NDArray[np.float32] = np.stack([root_zero_q] + [zero_q] * (self.joint_num - 1), axis=0)

        # 构建从根节点开始的所有节点名 [[root->a->b->...],[root->c->d->...],...]
        self.chain_joint_names_fron_root: List[List[str]] = []
        self._get_chain_name_from_root(cur_joint=self.root_joint, cur_sequence=None)
        # 构建从根节点开始的所有节点名和其对应的下标 [{根节点名:下标,孩子节点名:下标,孙子节点名:下标,...},{根节点名:下标,孩子节点名:下标,孙子节点名:下标,...},...]
        self.chain_joint_names_to_idx_dict_from_root: List[Dict[str, int]] = self._get_chain_names_to_idx_dict()

        self.cur_frame = 0  # initialize skeleton pose to first frame
        self.apply_frame(self.cur_frame)

    def get_joint_names(self) -> List[str]:
        """ Get names of joints in skeleton in the order in which BVH rotation data is stored. """
        return self.root_joint.get_chain_joint_names()

    def update(self) -> None:
        """Based upon internal time, determine which frame should be displayed and apply it"""
        cur_time: float = self.get_time()
        cur_frame = round(cur_time / self.frame_time) % self.frame_max_num
        self.apply_frame(cur_frame)

    def apply_frame(self, frame_num: int) -> None:
        """ Apply root position and joint rotation data for specified frame_num ,
            Specificaaly, if we set the frame_num < 0, we will get the init pose data
        """
        # 动画帧
        if frame_num >= 0:
            # Animated Frame
            self.root_joint.set_position(self.pos_data[frame_num])
            self._apply_frame_rotations(self.root_joint, frame_num, ptr=np.array(0))
        # 初始标准姿态帧
        else:
            # Init Pos Frame, here we default set frame index=-1
            self._apply_init_local_offset(self.root_joint, ptr=np.array(0))
            self._apply_frame_rotations(self.root_joint, frame_num, ptr=np.array(0))

    def _apply_frame_rotations(self, joint: BVH_Joint, frame_num: int, ptr: npt.NDArray[np.int32]) -> None:
        if frame_num >= 0:
            q = Quaternions(self.rot_data[frame_num, ptr])
        else:
            q = Quaternions(self.init_rot_data[ptr])
        joint.set_rotation(q)

        ptr += 1

        for c in joint.get_children():
            if not isinstance(c, BVH_Joint):
                continue
            self._apply_frame_rotations(c, frame_num, ptr)

    def get_skeleton_fwd(self, forward_perp_vector_joint_names: List[Tuple[str, str]], update: bool = True) -> Vectors:
        """
        Get current forward vector of skeleton in world coords. If update=True, ensure skeleton transforms are current.
        Input forward_perp_vector_joint_names, a list of pairs of joint names (e.g. [[leftshould, rightshoulder], [lefthip, righthip]])
        Finds average of vectors between joint pairs, then returns vector perpendicular to their average.
        """
        if update:
            self.root_joint.update_transforms(update_ancestors=True)

        vectors_cw_perpendicular_to_fwd: List[Vectors] = []
        for (start_joint_name, end_joint_name) in forward_perp_vector_joint_names:
            start_joint = self.root_joint.get_transform_by_name(start_joint_name)
            if not start_joint:
                msg = f'Could not find BVH joint with name: {start_joint}'
                logging.critical(msg)
                assert False, msg

            end_joint = self.root_joint.get_transform_by_name(end_joint_name)
            if not end_joint:
                msg = f'Could not find BVH joint with name: {end_joint}'
                logging.critical(msg)
                assert False, msg

            bone_vector: Vectors = Vectors(end_joint.get_world_position()) - Vectors(start_joint.get_world_position())
            bone_vector.norm()
            vectors_cw_perpendicular_to_fwd.append(bone_vector)

        return Vectors(vectors_cw_perpendicular_to_fwd).average().perpendicular()

    @classmethod
    def from_file(cls, bvh_fn: str, start_frame_idx: int = 0, end_frame_idx: Optional[int] = None,
                  init_root_rot_eular: Optional[npt.NDArray[np.float32]] = np.array([0.0, 0.0, 0.0])) -> BVH:
        """ Given a path to a .bvh, constructs and returns BVH object
            !!!
            Please attention: Here, please attention: If the bvh file is export from Blender use optimized IK in Blender,
            due to the up vector in Blender is diefferenct from
            default OpennGL default coordinate system(+z up and +y forward), you should set rotation of X axis data is
            90 degree for the root joint in T-pose state
            for instance,
            in our rotation order='ZXY', init_root_rot_eular should be [0.0 , 90.0 , 0.0] ,
            after that , the correct init pose is for the +y up and -z forward.
            Else, if you acquired bvh in other way, currently, you merely set rotation of T-pose is [0.0,0.0,0.0] is OK.
            !!!
        """

        # search for the BVH file specified
        bvh_p: Path = resolve_ad_filepath(bvh_fn, 'bvh file')
        logging.info(f'Using BVH file located at {bvh_p.resolve()}')

        with open(str(bvh_p), 'r') as f:
            lines = f.read().splitlines()

        if lines.pop(0) != 'HIERARCHY':
            msg = f'Malformed BVH in line preceding {lines}'
            logging.critical(msg)
            assert False, msg

        # Parse the skeleton
        # 这里主要是获得所有节点名和初始状态下的joint_name、offset、channel_order以及children List[BVH_Joint] (默认为准T字型)
        root_joint: BVH_Joint = BVH._parse_skeleton(lines)

        if lines.pop(0) != 'MOTION':
            msg = f'Malformed BVH in line preceding {lines}'
            logging.critical(msg)
            assert False, msg

        # Parse motion metadata
        frame_max_num = int(lines.pop(0).split(':')[-1])
        frame_time = float(lines.pop(0).split(':')[-1])

        # Parse motion data
        frames = [list(map(float, line.strip().split(' '))) for line in lines]
        if len(frames) != frame_max_num:
            msg = f'framenum specified ({frame_max_num}) and found ({len(frames)}) do not match'
            logging.critical(msg)
            assert False, msg

        # Split logically distinct root position data from joint euler angle rotation data
        pos_data: npt.NDArray[np.float32]
        rot_data: npt.NDArray[np.float32]
        pos_data, rot_data = BVH._process_frame_data(root_joint, frames)

        # Set end_frame if not passed in
        if not end_frame_idx:
            end_frame_idx = frame_max_num

        # Ensure end_frame_idx <= frame_max_num
        if frame_max_num < end_frame_idx:
            msg = f'config specified end_frame_idx > bvh frame_max_num ({end_frame_idx} > {frame_max_num}). Replacing with frame_max_num.'
            logging.warning(msg)
            end_frame_idx = frame_max_num

        # slice position and rotation data using start and end frame indices
        pos_data = pos_data[start_frame_idx:end_frame_idx, :]
        rot_data = rot_data[start_frame_idx:end_frame_idx, :]

        # new frame_max_num based is end_frame_idx minus start_frame_idx
        frame_max_num = end_frame_idx - start_frame_idx

        return BVH(bvh_p.name, root_joint, frame_max_num, frame_time, pos_data, rot_data, init_root_rot_eular)

    def get_joints_init_local_offset(self) -> npt.NDArray[np.float32]:
        '''
        在最初获取标准姿态时调用，得到的是每一个关节点相关的相对offset
        :return: List[(offset_x,offset_y,offset_z),...]
        所有offset组成的一个列表，每个元素由offset_x、offset_y和offset_z组成
        '''
        return self.root_joint.get_chain_joint_init_local_offset()

    @classmethod
    def _parse_skeleton(cls, lines: List[str]) -> BVH_Joint:
        """
        Called recursively to parse and construct skeleton from BVH
        :param lines: partially-processed contents of BVH file. Is modified in-place.
        :return: Joint,init_pos_data(Represent in init offset)
        """

        # Get the joint name
        if lines[0].strip().startswith('ROOT'):
            _, joint_name = lines.pop(0).strip().split(' ')
        elif lines[0].strip().startswith('JOINT'):
            _, joint_name = lines.pop(0).strip().split(' ')
        elif lines[0].strip().startswith('End Site'):
            joint_name = lines.pop(0).strip()
        else:
            msg = f'Malformed BVH. Line: {lines[0]}'
            logging.critical(msg)
            assert False, msg

        if lines.pop(0).strip() != '{':
            msg = f'Malformed BVH in line preceding {lines}'
            logging.critical(msg)
            assert False, msg

        # Get offset
        if not lines[0].strip().startswith('OFFSET'):
            msg = f'Malformed BVH in line preceding {lines}'
            logging.critical(msg)
            assert False, msg
        _, *xyz = lines.pop(0).strip().split(' ')
        offset = Vectors(list(map(float, xyz)))
        # Get channels
        if lines[0].strip().startswith('CHANNELS'):
            channel_order = lines.pop(0).strip().split(' ')
            _, channel_num, *channel_order = channel_order
        else:
            channel_num, channel_order = 0, []
        if int(channel_num) != len(channel_order):
            msg = f'Malformed BVH in line preceding {lines}'
            logging.critical(msg)
            assert False, msg

        # Recurse for children
        children: List[BVH_Joint] = []
        while lines[0].strip() != '}':
            children.append(BVH._parse_skeleton(lines))
        lines.pop(0)  # }

        return BVH_Joint(name=joint_name, offset=offset, channel_order=channel_order, children=children)

    @classmethod
    def _process_frame_data(cls, skeleton: BVH_Joint, frames: List[List[float]]) -> Tuple[
        npt.NDArray[np.float32], npt.NDArray[np.float32]]:
        """ Given skeleton and frame data, return root position data and joint quaternion data, separately"""

        def _get_frame_channel_order(joint: BVH_Joint, channels=[]):
            channels.extend(joint.channel_order)
            for child in [child for child in joint.get_children() if isinstance(child, BVH_Joint)]:
                _get_frame_channel_order(child, channels)
            return channels

        channels = _get_frame_channel_order(skeleton)

        # create a mask so we retain only joint rotations and root position
        mask = np.array(list(map(lambda x: True if 'rotation' in x else False, channels)))
        mask[:3] = True  # hack to make sure we keep root position

        frames = np.array(frames, dtype=np.float32)[:, mask]

        # split root pose data and joint euler angle data
        pos_data, ea_rots = np.split(np.array(frames, dtype=np.float32), [3], axis=1)

        # quaternion rot data will go here
        rot_data = np.empty([len(frames), skeleton.joint_count(), 4], dtype=np.float32)
        BVH._pose_ea_to_q(skeleton, ea_rots, rot_data)

        return pos_data, rot_data

    @classmethod
    def _pose_ea_to_q(cls, joint: BVH_Joint, ea_rots: npt.NDArray[np.float32], q_rots: npt.NDArray[np.float32],
                      p1: int = 0, p2: int = 0) -> Tuple[int, int]:
        """
        Given joint and array of euler angle rotation data, converts to quaternions and stores in q_rots.
        Only called by _process_frame_data(). Modifies q_rots inplace.
        :param p1: pointer to find where in ea_rots to read euler angles from
        :param p2: pointer to determine where in q_rots to input quaternion
        """
        axis_chars = "".join([c[0].lower() for c in joint.channel_order if c.endswith('rotation')])  # e.g. 'xyz'

        q_rots[:, p2] = Quaternions.from_euler_angles(axis_chars, ea_rots[:, p1:p1 + len(axis_chars)]).qs
        p1 += len(axis_chars)
        p2 += 1

        for child in joint.get_children():
            if isinstance(child, BVH_Joint):
                p1, p2 = BVH._pose_ea_to_q(child, ea_rots, q_rots, p1, p2)

        return p1, p2

    def _get_chain_name_from_root(self, cur_joint: Union[Joint, Transform], cur_sequence: Union[List[str], None]):
        '''
        使用DFS从根节点开始向下遍历各个层次树,得到的是各个分之路的字符串序列
        :param cur_joint:
        :param cur_sequence:
        :return:
        '''
        # 特殊处理空值(这个是因为使用的BVH类库中结束节点为None)
        if cur_joint is None:
            return

        # 结束标志
        if cur_joint.name in BVH.END_JOINT_NAME:
            self.chain_joint_names_fron_root.append(deepcopy(cur_sequence))
            cur_sequence = cur_sequence[:-1]
            return

        # 根节点开始，则创建新的序列
        if cur_joint.name == self.root_joint.name:
            cur_sequence = []
            cur_sequence.append(self.root_joint.name)

        for next_joint in cur_joint.get_children():
            cur_sequence.append(next_joint.name)
            self._get_chain_name_from_root(cur_joint=next_joint,
                                           cur_sequence=cur_sequence)
            cur_sequence.pop()

    def _get_chain_names_to_idx_dict(self):
        '''
        从根节点出发，根据每条获取链路的节点名称得到对应的 名称和下标字典对列表
        :return: List[Dict[str, int]] 即
        [[{根节点名称:下标},{孩子节点名:下标},{孙子节点名:下标}],[{根节点名称:下标},{孩子节点名:下标},{孙子节点名:下标}],...,]
        '''
        ref_joint_names_list: List[str] = self.get_joint_names()
        chain_joint_names_with_idx_dict: List[Dict[str, int]] = []
        all_endsite_indicies: List[int] = [idx for idx, name in enumerate(ref_joint_names_list) if
                                           name in BVH.END_JOINT_NAME]

        endsite_repeate_num = 0
        for cur_sequence in self.chain_joint_names_fron_root:
            cur_name_with_idx_dict: Dict[str, int] = {}
            for name in cur_sequence:
                if name in BVH.END_JOINT_NAME:
                    cur_name_with_idx_dict[name] = all_endsite_indicies[endsite_repeate_num]
                    endsite_repeate_num += 1
                else:
                    cur_name_with_idx_dict[name] = ref_joint_names_list.index(name)
            chain_joint_names_with_idx_dict.append(cur_name_with_idx_dict)

        return chain_joint_names_with_idx_dict

    def _apply_init_local_offset(self, joint: BVH_Joint, ptr: npt.NDArray[np.int32]) -> None:
        '''
        重置所有节点的offset，使得其恢复至T字形
        :param joint:
        :param ptr:
        :return:
        '''
        init_offset: Vectors = Vectors(self.init_local_offset[ptr])
        joint.reset_offset(init_offset)

        ptr += 1

        for c in joint.get_children():
            if not isinstance(c, BVH_Joint):
                continue
            self._apply_init_local_offset(c, ptr)
