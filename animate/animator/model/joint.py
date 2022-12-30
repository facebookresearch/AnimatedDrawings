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
        """ Returns the number of Joint children in this joint's kinematic chain(recursive) """
        count = 1
        for c in self.get_children():
            if isinstance(c, Joint):
                count += c.joint_count()
        return count
    
    def get_joint_by_name(self, name: str) -> Optional[Joint]:
        """ Search self and joint children for joint with matching name. Return it if found, None otherwise. """

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
