from __future__ import annotations
from animator.model.transform import Transform
from typing import Optional


class Joint(Transform):
    """
    Skeletal joint used representing character poses.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def joint_count(self):
        """ Returns 1 + the number of Joint children in this joint's kinematic chain (recursive) """
        count = 1
        for c in self.get_children():
            if isinstance(c, Joint):
                count += c.joint_count()
        return count

    def get_chain_worldspace_positions(self):
        """ Get xzy worldspace coordinates of all joints within the chain. """
        self.update_transforms(update_ancestors=True)
        return self._get_chain_worldspace_positions(self, [])

    def _get_chain_worldspace_positions(self, joint: Joint, position_list: list):
        position_list.extend(joint.get_world_position(update_ancestors=False))
        for c in joint.get_children():
            if not isinstance(c, Joint):
                continue
            self._get_chain_worldspace_positions(c, position_list)
        return position_list

    def get_chain_joint_names(self):
        """ Traverse through joint in depth-first order and return names of joints in the order they are visited. """
        joint_names: list = []
        return self._get_chain_joint_names(self, joint_names)

    def _get_chain_joint_names(self, joint: Joint, joint_name_list: list):
        joint_name_list.append(joint.name)
        for c in joint.get_children():
            if not isinstance(c, Joint):
                continue
            self._get_chain_joint_names(c, joint_name_list)
        return joint_name_list

    def get_joint_by_name(self, name: str) -> Optional[Joint]:
        """ Search self and joint children for joint with matching name. Return it if found, None otherwise. """
        # TODO: Make this a Transform method. No reason to restrict to just joints.

        # are we match?
        if self.name == name:
            return self

        # recurse to check if a child is match
        for c in self.get_children():
            if isinstance(c, Joint):
                joint_or_none = c.get_joint_by_name(name)
                if joint_or_none:  # if we found it
                    return joint_or_none

        # no match
        return None
