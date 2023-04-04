# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import annotations
from animated_drawings.model.transform import Transform
from typing import List


class Joint(Transform):
    """
    Skeletal joint used representing character poses.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def joint_count(self) -> int:
        """ Returns 1 + the number of Joint children in this joint's kinematic chain (recursive) """
        count: int = 1
        for c in self.get_children():
            if isinstance(c, Joint):
                count += c.joint_count()
        return count

    def get_chain_worldspace_positions(self) -> List[float]:
        """ Get xzy worldspace coordinates of all joints within the chain. """
        self.update_transforms(update_ancestors=True)
        return self._get_chain_worldspace_positions(self, [])

    def _get_chain_worldspace_positions(self, joint: Joint, position_list: List[float]) -> List[float]:
        position_list.extend(joint.get_world_position(update_ancestors=False))
        for c in joint.get_children():
            if not isinstance(c, Joint):
                continue
            self._get_chain_worldspace_positions(c, position_list)
        return position_list

    def get_chain_joint_names(self):
        """ Traverse through joint in depth-first order and return names of joints in the order they are visited. """
        joint_names: List[str] = []
        return self._get_chain_joint_names(self, joint_names)

    def _get_chain_joint_names(self, joint: Joint, joint_name_list: List[str]) -> List[str]:
        joint_name_list.append(str(joint.name))
        for c in joint.get_children():
            if not isinstance(c, Joint):
                continue
            self._get_chain_joint_names(c, joint_name_list)
        return joint_name_list
