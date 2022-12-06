import numpy as np
from model.vectors import Vectors
import logging


class Transform():
    """Base class from which all other scene objects descend"""

    def __init__(self):
        self.transform = np.identity(4)
        self.children = []

    def set_position(self, pos: Vectors):
        if pos.vs.shape != (1, 3):
            logging.critical(f'pos vector must have shape [1,3]. Found: {pos.vs.shape}')
            assert False
        self.transform[:-1, -1] = pos.vs

    def look_at(self, fwd: Vectors):
        """Given a forward vector, rotate the transform to face that position without affect scale or translation"""

        if fwd.vs.shape != (1, 3):
            logging.critical(f'look_at fwd vector must have shape [1,3]. Found: {fwd.vs.shape}')
            assert False

        fwd_n: Vectors = fwd.copy()
        fwd_n.norm()
        tmp: Vectors = Vectors([0, 1, 0])
        right: Vectors = tmp.cross(fwd)
        up: Vectors = fwd.cross(right)

        self.transform[:-1, 0] = right.vs
        self.transform[:-1, 1] = up.vs
        self.transform[:-1, 2] = fwd.vs

    def add_child(self, child):
        """Child must be another transform or subclass thereof"""
        self.children.append(child)

    def draw(self, recurse=True, **kwargs):
        self._draw(**kwargs)
        if not recurse:
            return
        [child.draw(recurse=recurse, **kwargs) for child in self.children]

    def _draw(self, **kwargs):
        """Transforms default to not being drawn. Subclasses must implement how they appear"""
        pass
