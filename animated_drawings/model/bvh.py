# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import annotations  # so we can refer to class Type inside class
import logging
from pathlib import Path
from typing import List, Tuple, Optional

import numpy as np
import numpy.typing as npt

from animated_drawings.model.transform import Transform
from animated_drawings.model.box import Box
from animated_drawings.model.quaternions import Quaternions
from animated_drawings.model.vectors import Vectors
from animated_drawings.model.joint import Joint
from animated_drawings.model.time_manager import TimeManager
from animated_drawings.utils import resolve_ad_filepath


class BVH_Joint(Joint):
    """
        Joint class with channel order attribute and specialized vis widget
    """
    def __init__(self, channel_order: List[str] = [], widget: bool = True, **kwargs) -> None:
        super().__init__(**kwargs)

        self.channel_order = channel_order

        self.widget: Optional[Transform] = None
        if widget:
            self.widget = Box()
            self.add_child(self.widget)

    def _draw(self, **kwargs):
        if self.widget:
            self.widget.draw(**kwargs)


class BVH(Transform, TimeManager):
    """
    Class to encapsulate BVH (Biovision Hierarchy) animation data.
    Include a single skeletal hierarchy defined in the BVH, frame count and speed,
    and skeletal pos/rot data for each frame
    """

    def __init__(self,
                 name: str,
                 root_joint: BVH_Joint,
                 frame_max_num: int,
                 frame_time: float,
                 pos_data: npt.NDArray[np.float32],
                 rot_data: npt.NDArray[np.float32]
                 ) -> None:
        """
        Don't recommend calling this method directly.  Instead, use BVH.from_file().
        """
        super().__init__()

        self.name: str = name
        self.frame_max_num: int = frame_max_num
        self.frame_time: float = frame_time
        self.pos_data: npt.NDArray[np.float32] = pos_data
        self.rot_data: npt.NDArray[np.float32] = rot_data

        self.root_joint = root_joint
        self.add_child(self.root_joint)
        self.joint_num = self.root_joint.joint_count()

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
        """ Apply root position and joint rotation data for specified frame_num """
        self.root_joint.set_position(self.pos_data[frame_num])
        self._apply_frame_rotations(self.root_joint, frame_num, ptr=np.array(0))

    def _apply_frame_rotations(self, joint: BVH_Joint, frame_num: int, ptr: npt.NDArray[np.int32]) -> None:
        q = Quaternions(self.rot_data[frame_num, ptr])
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
    def from_file(cls, bvh_fn: str, start_frame_idx: int = 0, end_frame_idx: Optional[int] = None) -> BVH:
        """ Given a path to a .bvh, constructs and returns BVH object"""

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

        return BVH(bvh_p.name, root_joint, frame_max_num, frame_time, pos_data, rot_data)

    @classmethod
    def _parse_skeleton(cls, lines: List[str]) -> BVH_Joint:
        """
        Called recursively to parse and construct skeleton from BVH
        :param lines: partially-processed contents of BVH file. Is modified in-place.
        :return: Joint
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
    def _process_frame_data(cls, skeleton: BVH_Joint, frames: List[List[float]]) -> Tuple[npt.NDArray[np.float32], npt.NDArray[np.float32]]:
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
    def _pose_ea_to_q(cls, joint: BVH_Joint, ea_rots: npt.NDArray[np.float32], q_rots: npt.NDArray[np.float32], p1: int = 0, p2: int = 0) -> Tuple[int, int]:
        """
        Given joint and array of euler angle rotation data, converts to quaternions and stores in q_rots.
        Only called by _process_frame_data(). Modifies q_rots inplace.
        :param p1: pointer to find where in ea_rots to read euler angles from
        :param p2: pointer to determine where in q_rots to input quaternion
        """
        axis_chars = "".join([c[0].lower() for c in joint.channel_order if c.endswith('rotation')])  # e.g. 'xyz'

        q_rots[:, p2] = Quaternions.from_euler_angles(axis_chars, ea_rots[:, p1:p1+len(axis_chars)]).qs
        p1 += len(axis_chars)
        p2 += 1

        for child in joint.get_children():
            if isinstance(child, BVH_Joint):
                p1, p2 = BVH._pose_ea_to_q(child, ea_rots, q_rots, p1, p2)

        return p1, p2
