from __future__ import annotations  # so we can refer to class Type inside class
import numpy as np
import logging
from typing import Union
from numbers import Number
from copy import copy
from utils import tolerance


class Vectors():
    """
    Wrapper class around ndarray interpreted as one or more vectors of equal dimensionality
    When passing in existing Vectors, new Vectors object will share the underlying nparray, so be careful.
    """

    def __init__(self, vs_: Union[tuple, list, np.ndarray, Vectors]):
        # initialize from single ndarray
        if isinstance(vs_, np.ndarray):
            if len(vs_.shape) == 1:
                vs_ = np.expand_dims(vs_, axis=0)
            vs = vs_

        # initialize from tuple or list of numbers
        elif isinstance(vs_, (tuple, list)) and isinstance(vs_[0], Number):
            try:
                vs_ = np.array(vs_)
                if len(vs_.shape) == 1:
                    vs_ = np.expand_dims(vs_, axis=0)
            except Exception as e:
                msg = f'Error initializing Vectors: {str(e)}'
                logging.critical(msg)
                assert False, msg
            vs = vs_

        # initialize from tuple or list of ndarrays
        elif isinstance(vs_, (tuple, list)) and isinstance(vs_[0], np.ndarray):
            try:
                vs_ = np.stack(vs_)
            except Exception as e:
                msg = f'Error initializing Vectors: {str(e)}'
                logging.critical(msg)
                assert False, msg
            vs = vs_

        # initialize from tuple or list of Vectors
        elif isinstance(vs_, (tuple, list)) and isinstance(vs_[0], Vectors):
            try:
                vs_ = np.stack([v.vs.squeeze() for v in vs_])
            except Exception as e:
                msg = f'Error initializing Vectors: {str(e)}'
                logging.critical(msg)
                assert False, msg
            vs = vs_

        # initialize from single Vectors
        elif isinstance(vs_, Vectors):
            vs: np.ndarray = vs_.vs

        else:
            msg = 'Vectors must be constructed from Vectors or numpy array'
            logging.critical(msg)
            assert False, msg

        self.vs: np.ndarray = vs

    def norm(self):
        ns = np.linalg.norm(self.vs, axis=-1)

        if np.min(ns) < tolerance:
            logging.info(f"Encountered values close to zero in vector norm. Replacing with {tolerance}")
            print(f"Encountered values close to zero in vector norm. Replacing with {tolerance}")
            ns[ns < tolerance] = tolerance

        self.vs = self.vs / np.expand_dims(ns, axis=-1)

    def cross(self, v2: Vectors):
        """ Cross product of a series of 2 or 3 dimensional vectors. All dimensions of vs must match."""

        if self.vs.shape != v2.vs.shape:
            msg = f'Cannot cross product different sized vectors: {self.vs.shape} {v2.vs.shape}.'
            logging.critical(msg)
            assert False, msg

        if not self.vs.shape[-1] in [2, 3]:
            msg = f'Cannot cross product vectors of size: {self.vs.shape[-1]}. Must be 2 or 3.'
            logging.critical(msg)
            assert False, msg

        return Vectors(np.cross(self.vs, v2.vs))

    def perpendicular(self, ccw=True):
        """
        Returns ndarray of vectors perpendicular to the original ones.
        Only 2D and 3D vectors are supported.
        By default returns the counter clockwise vector, but passing ccw=False returns clockwise
        """
        if not self.vs.shape[-1] in [2, 3]:
            msg = f'Cannot get perpendicular of vectors of size: {self.vs.shape[-1]}. Must be 2 or 3.'
            logging.critical(msg)
            assert False, msg

        v_up: Vectors = Vectors(np.tile([0.0, 1.0, 0.0], [*self.shape[:-1], 1]))

        v_perp = v_up.cross(self)
        v_perp.norm()

        if not ccw:
            v_perp *= -1

        return v_perp

    def average(self) -> Vectors:
        """ Return the average of a collection of vectors, along the first axis"""
        return Vectors(np.mean(self.vs, axis=0))

    @property
    def shape(self):
        return self.vs.shape

    @property
    def length(self):
        return np.linalg.norm(self.vs, axis=-1)

    def __mul__(self, val: float) -> Vectors:
        return Vectors(self.vs * val)

    def __truediv__(self, scale: Union[int, float]) -> Vectors:
        return Vectors(self.vs / scale)

    def __sub__(self, other: Vectors) -> Vectors:
        if self.vs.shape != other.vs.shape:
            msg = 'Attempted to subtract Vectors with different dimensions'
            logging.critical(msg)
            assert False, msg
        return Vectors(np.subtract(self.vs, other.vs))

    def __add__(self, other: Vectors) -> Vectors:
        if self.vs.shape != other.vs.shape:
            msg = 'Attempted to add Vectors with different dimensions'
            logging.critical(msg)
            assert False, msg
        return Vectors(np.add(self.vs, other.vs))

    def copy(self) -> Vectors:
        return copy(self)

    def __copy__(self) -> Vectors:
        return Vectors(self)

    def __str__(self) -> str:
        return f"Vectors({str(self.vs)})"

    def __repr__(self) -> str:
        return f"Vectors({str(self.vs)})"
