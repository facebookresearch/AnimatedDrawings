from __future__ import annotations  # so we can refer to class Type inside class
from pathlib import Path
from model.transform import Transform
from typing import List, Tuple
from model.box import Box
from model.quaternions import Quaternions
from model.vectors import Vectors
from model.joint import Joint
import numpy as np
import logging


class BVH_Joint(Joint):
    """
        Joint class with channel order attribute and specialized vis widget
    """
    def __init__(self, channel_order: List[str] = [], widget: bool = False, **kwargs):
        super().__init__(**kwargs)

        self.channel_order = channel_order

        if widget:
            self.widget = Box()
            self.add_child(self.widget)

    def _draw(self, **kwargs):
        if self.widget:
            self.widget.draw(**kwargs)


class BVH(Transform):
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
                 pos_data: np.ndarray,
                 rot_data: np.ndarray
                 ):
        """
        Do NOT call this method directly.  Use BVH.from_file() or another class method to construct a BVH object
        """
        super().__init__()

        self.name: str = name
        self.frame_max_num: int = frame_max_num
        self.frame_time: float = frame_time
        self.pos_data: np.ndarray = pos_data
        self.rot_data: np.ndarray = rot_data

        self.root_joint = root_joint
        self.add_child(self.root_joint)

        self.cur_frame = 0
        self.apply_frame(self.cur_frame)

    def apply_frame(self, frame_num: int) -> None:
        """
        Apply a the pose data from  
        """
        if not 0 <= frame_num < self.frame_max_num:
            msg = f'bad frame_num specified:{frame_num}. Must be between 0 and {self.frame_max_num}'
            logging.critical(msg)
            assert False, msg

        self.root_joint.set_position(self.pos_data[frame_num])
        self._apply_frame(self.root_joint, frame_num, ptr=np.array(0))

    def _apply_frame(self, joint: BVH_Joint, frame_num: int, ptr: np.ndarray):
        q = Quaternions(self.rot_data[frame_num, ptr])
        joint.set_rotate(q)

        ptr += 1

        for c in joint.get_children():
            if not isinstance(c, BVH_Joint):
                continue
            self._apply_frame(c, frame_num, ptr)

    @classmethod
    def from_file(cls, bvh_fn: str) -> BVH:
        """ Given a path to a .bvh, constructs and returns BVH object"""

        if not Path(bvh_fn).exists():
            msg = f'bvh_fn DNE: {bvh_fn}'
            logging.critical(msg)
            assert False, msg
        name = Path(bvh_fn).name

        with open(bvh_fn, 'r') as f:
            lines = f.read().splitlines()

        if lines.pop(0) != 'HIERARCHY':
            msg = f'Malformed BVH in line preceeding {lines}'
            logging.critical(msg)
            assert False, msg

        # Parse the skeleton
        root_joint: BVH_Joint = BVH._parse_skeleton(lines)

        if lines.pop(0) != 'MOTION':
            msg = f'Malformed BVH in line preceeding {lines}'
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
        pos_data, rot_data = BVH._process_frame_data(root_joint, frames)

        return BVH(name, root_joint, frame_max_num, frame_time, pos_data, rot_data)

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
            msg = f'Malformed BVH in line preceeding {lines}'
            logging.critical(msg)
            assert False, msg

        # Get offset
        if not lines[0].strip().startswith('OFFSET'):
            msg = f'Malformed BVH in line preceeding {lines}'
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
            msg = f'Malformed BVH in line preceeding {lines}'
            logging.critical(msg)
            assert False, msg

        # Recurse for children
        children = []
        while lines[0].strip() != '}':
            children.append(BVH._parse_skeleton(lines))
        lines.pop(0)  # }

        return BVH_Joint(name=joint_name, offset=offset, channel_order=channel_order, children=children)

    @classmethod
    def _process_frame_data(cls, skeleton: BVH_Joint, frames: List[List[float]]) -> Tuple[np.ndarray, np.ndarray]:
        """ Given skeleton and frame data, return root position data and joint quaternion data, separately"""

        # split root pose data and joint euler angle data
        pos_data, ea_rots = np.split(np.array(frames, dtype=np.float32), [3], axis=1)

        # modify pos_data so the character root is positioned at origin for the first frame
        pos_data -= pos_data[0]

        # quaternion rot data will go here
        rot_data = np.empty([len(frames), skeleton.joint_count(), 4], dtype=np.float32)
        BVH._pose_ea_to_q(skeleton, ea_rots, rot_data)

        return pos_data, rot_data

    @classmethod
    def _pose_ea_to_q(cls, joint: BVH_Joint, ea_rots: np.ndarray, q_rots: np.ndarray, p1: int = 0, p2: int = 0):
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
