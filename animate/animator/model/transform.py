import numpy as np
from model.vector import Vector


class Transform():
    """Base class from which all other scene objects descend"""

    def __init__(self):
        self.transform = np.identity(4)
        self.children = []

    def set_position(self, pos: Vector):
        self.transform[:-1, -1] = pos.data

    def look_at(self, fwd: Vector):
        """Given a forward vector, rotate the transform to face that position without affect scale or translation"""
        # Follow this: https://www.scratchapixel.com/lessons/mathematics-physics-for-computer-graphics/lookat-function
        # but use column major not row major
        fwd_n: Vector = fwd.copy()
        fwd_n.norm()
        tmp: Vector = Vector(0, 1, 0)
        right: Vector = tmp.cross(fwd)
        up: Vector = fwd.cross(right)

        self.transform[:-1, 0] = right.data
        self.transform[:-1, 1] = up.data
        self.transform[:-1, 2] = fwd.data

    def add_child(self, child):
        """Child must be another transform or subclass thereof"""
        self.children.append(child)
