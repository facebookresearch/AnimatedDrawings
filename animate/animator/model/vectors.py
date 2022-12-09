from __future__ import annotations  # so we can refer to class Type inside class
import numpy as np
from numbers import Number
import logging
from typing import Union
from copy import copy
from utils import tolerance


class Vectors():
    """
    Wrapper class around ndarray interpreted as one or more vectors of equal dimensionality
    When passing in existing Vectors, new Vectors object will share the underlying nparray, so be careful.
    """

    def __init__(self, vs: Union[tuple, list, np.ndarray, Vectors]):
        if isinstance(vs, np.ndarray):
            if len(vs.shape) == 1:
                vs = np.expand_dims(vs, axis=0)
            self.vs: np.ndarray = vs

        elif isinstance(vs, tuple) or isinstance(vs, list):
            try:
                vs = np.array(vs)
            except Exception:
                msg = 'Could not convert vector data to ndarray'
                logging.critical(msg)
                assert False, msg

            if len(vs.shape) == 1:
                vs = np.expand_dims(vs, axis=0)
            self.vs: np.ndarray = vs

        elif isinstance(vs, Vectors):
            self.vs: np.ndarray = vs.vs

        else:
            msg = 'Vectors must be constructed from Vectors or numpy array'
            logging.critical(msg)
            assert False, msg

    def __div__(self, scale: Number):
        return Vectors(self.vs / scale)

    def copy(self):
        return copy(self)

    def __copy__(self):
        return Vectors(self)

    def norm(self):
        ns = np.linalg.norm(self.vs, axis=-1)

        if np.min(ns) < tolerance:
            logging.info(f"Encountered values close to zero in vector norm. Replacing with {tolerance}")
            print(f"Encountered values close to zero in vector norm. Replacing with {tolerance}")
            ns[ns < tolerance] = tolerance

        self.vs = self.vs / np.expand_dims(ns, axis=-1)

    def cross(self, v2):
        assert isinstance(v2, Vectors)

        if self.vs.shape != v2.vs.shape:
            msg = f'Cannot cross product different sized vectors: {self.vs.shape} {v2.vs.shape}.'
            logging.critical(msg)
            assert False, msg

        if not self.vs.shape[-1] in [2, 3]:
            msg = f'Cannot cross product vectors of size: {self.vs.shape[-1]}. Must be 2 or 3.'
            logging.critical(msg)
            assert False, msg

        return Vectors(np.cross(self.vs, v2.vs))

    def __str__(self):
        return f"Vectors({str(self.vs)})"

    def __repr__(self):
        return f"Vectors({str(self.vs)})"


if __name__ == '__main__':

    # test1
    # try with multidimensional vector.shape = [2, 3, 3, 3]
    v1 = Vectors(np.array([
            [
                [[0, 1, 2], [1, 2, 3], [2, 3, 4]],
                [[0, 1, 2], [1, 2, 3], [2, 3, 4]],
                [[0, 1, 2], [1, 2, 3], [2, 3, 4]],
            ],
            [
                [[0, 1, 2], [1, 2, 3], [2, 3, 4]],
                [[0, 1, 2], [1, 2, 3], [2, 3, 4]],
                [[0, 1, 2], [1, 2, 3], [2, 3, 4]],
            ]
        ]))
    v1.norm()

    # test2
    # crossproduct test
    v2 = Vectors(np.array([
        [
            [[0, 1, 2], [1, 2, 3], [2, 3, 4]],
            [[0, 1, 2], [1, 2, 3], [2, 3, 4]],
            [[0, 1, 2], [1, 2, 3], [2, 3, 4]],
        ],
        [
            [[0, 1, 2], [1, 2, 3], [2, 3, 4]],
            [[0, 1, 2], [1, 2, 3], [2, 3, 4]],
            [[0, 1, 2], [1, 2, 3], [2, 3, 4]],
        ]
    ]))

    v3 = Vectors(np.array([
        [
            [[0, 1, 2], [1, 2, 3], [2, 3, 4]],
            [[0, 1, 2], [1, 2, 3], [2, 3, 4]],
            [[0, 1, 2], [1, 2, 3], [2, 3, 4]],
        ],
        [
            [[0, 1, 2], [1, 2, 3], [2, 3, 4]],
            [[0, 1, 2], [1, 2, 3], [2, 3, 4]],
            [[0, 1, 2], [1, 2, 3], [2, 3, 4]],
        ]
    ]))

    print(v2.cross(v3))
