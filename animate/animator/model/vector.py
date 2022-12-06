import numpy as np
from numbers import Number
import logging
from copy import copy


class Vector():

    def __init__(self, *args):
        if len(args) == 1 and type(args[0]) == np.ndarray:  # if passed an ndarray, copy it's contents into data
            self.data = np.copy(args[0])
        else:
            self.data = np.array(args)

    def __div__(self, scale: Number):
        return Vector(self.data / scale)  # type: ignore

    def copy(self):
        return copy(self)

    def __copy__(self):
        return Vector(*self.data)

    def norm(self):
        self.data = self.data / np.linalg.norm(self.data)

    def cross(self, v2):
        assert isinstance(v2, Vector)

        if self.data.shape != v2.data.shape:
            logging.critical(
                'Attempted to get cross product of different sized vectors. Aborting.')
            assert False

        return Vector(np.cross(self.data, v2.data))

    def __str__(self):
        return str(self.data)
