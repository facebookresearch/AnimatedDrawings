from __future__ import annotations  # so we can refer to class Type inside class
from pathlib import Path
from model.transform import Transform
from typing import List
from model.box import Box
from model.quaternions import Quaternions
from model.vectors import Vectors
import numpy as np
import logging


class Joint(Transform):
    def __init__(self,
                 joint_name: str,
                 offset: Vectors,
                 channel_order: List[str],
                 children: List[Joint]
                 ):
        super().__init__()

        self.name = joint_name

        self.offset(offset)

        self.channel_order = channel_order

        for c in children:
            self.add_child(c)  # TODO:  Differential joint children from non-joint children

        self.widget = Box()
        self.add_child(self.widget) # TODO:  Differential joint children from non-joint children

    def _draw(self):
        self.widget.draw()


class BVH(Transform):

    def __init__(self, bvh_fn: str):
        super().__init__()

        if not Path(bvh_fn).exists():
            msg = f'bvh_fn DNE: {bvh_fn}'
            logging.critical(msg)
            assert False, msg

        with open(bvh_fn, 'r') as f:
            lines = f.read().split('\n')[:-1]  # drop final string, empty

        assert lines.pop(0) == 'HIERARCHY', f'Malformed BVH 1'

        self.root_joint = self.parse_skeleton(lines)
        self.add_child(self.root_joint)

        assert lines.pop(0) == 'MOTION', f'Malformed BVH 6'

        self.frame_num = int(lines.pop(0).strip().split(':')[1])
        self.frame_time = float(lines.pop(0).strip().split(':')[1])

        frames = []
        while lines:
            frames.append(list(map(float, lines.pop(0).strip().split(' '))))
        assert len(frames) == self.frame_num

        self.pos_data, self.rot_data_ = np.split(np.array(frames, dtype=np.float32), [3], axis=1)

        self.rots = np.empty([len(frames), self.joint_num, 4], dtype=np.float32)

        self.parse_frame_data(self.root_joint)

    @property
    def joint_num(self):
        return self._joint_count(self.root_joint)

    def _joint_count(self, joint: Joint):
        count = 1
        for c in joint._children:
            if type(c) == Joint:
                count += self._joint_count(c)
        return count

    def apply_frame(self, frame_num: int):
        if not 0 <= frame_num < self.frame_num:
            raise ValueError(f'bad frame_num specified:{frame_num}. Must be between 0 and {self.frame_num}')

        self.root_joint.set_translate(self.pos_data[frame_num])
        self._apply_frame(self.root_joint, frame_num, ptr=[0])

        self.root_joint.update_transforms()

    def _apply_frame(self, joint, frame_num, ptr=[0]):

        joint.set_rotate(Quaternions(self.rots[frame_num, ptr]))
        ptr[0] += 1

        for c in joint._children:
            if not type(c) == Joint:
                continue
            self._apply_frame(c, frame_num, ptr)

    def parse_skeleton(self, lines: List[str]) -> Joint:
        """
        Called by __init__, and recursively, to parse and construct skeleton from BVH
        :param lines: partially-processed contents of BVH file
        :return: Joint
        """

        if lines[0].strip().startswith('ROOT') or lines[0].strip().startswith('JOINT'):
            _, joint_name = lines.pop(0).strip().split(' ')
        elif lines[0].strip().startswith('End Site'):
            joint_name = lines.pop(0).strip()
        else:
            assert False, f'Malformed BVH 7'

        assert lines.pop(0).strip() == '{', f'Malformed BVH 2'

        if lines[0].strip().startswith('OFFSET'):
            _, x, y, z = lines.pop(0).strip().split(' ')
            offset = list(map(float, [x, y, z]))
        else:
            offset = [0, 0, 0]

        if lines[0].strip().startswith('CHANNELS'):
            channel_order = lines.pop(0).strip().split(' ')
            _ = channel_order.pop(0)
            num = int(channel_order.pop(0))
            assert num == len(channel_order), f'Malformed BVH 5'
        else:
            channel_order = []

        children = []
        while lines[0].strip() != '}':
            children.append(self.parse_skeleton(lines))

        assert lines.pop(0).strip() == '}'

        return Joint(joint_name, offset, channel_order, children)

    def parse_frame_data(self, joint, p1=0, p2=0):
        """
        :param joint: root joint to be traversed
        :param p1: pointer to find where in self.rot_data_ to read angles from
        :param p2: pointer to determine where in self.rots to input quaternion
        :return:
        """

        axis_chars = []
        for c in joint.channel_order:
            if c.endswith('position'):
                continue

            axis_chars.append(c[0].lower())

        self.rots[:, p2] = Quaternions.from_euler_angles("".join(axis_chars), self.rot_data_[:, p1:p1+len(axis_chars)]).qs
        p1 += len(axis_chars)
        p2 += 1

        for child in joint._children:
            if type(child) != Joint:
                continue
            p1, p2 = self.parse_frame_data(child, p1, p2)

        return p1, p2


if __name__ == '__main__':
    print('hello world')