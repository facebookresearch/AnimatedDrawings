# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import annotations  # so we can refer to class Type inside class
import numpy as np
import numpy.typing as npt
import logging
from typing import Union, Iterable, Tuple
from numbers import Number
from copy import copy
from animated_drawings.utils import TOLERANCE


class Vectors():
    """
    Wrapper class around ndarray interpreted as one or more vectors of equal dimensionality
    When passing in existing Vectors, new Vectors object will share the underlying nparray, so be careful.
    """

    def __init__(self, vs_: Union[Iterable[Union[float, int, Vectors, npt.NDArray[np.float32]]], Vectors]) -> None:  # noqa: C901

        self.vs: npt.NDArray[np.float32]

        # initialize from single ndarray
        if isinstance(vs_, np.ndarray):
            if len(vs_.shape) == 1:
                vs_ = np.expand_dims(vs_, axis=0)
            self.vs = vs_

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
            self.vs = vs_

        # initialize from tuple or list of ndarrays
        elif isinstance(vs_, (tuple, list)) and isinstance(vs_[0], np.ndarray):
            try:
                vs_ = np.stack(vs_)  # pyright: ignore[reportGeneralTypeIssues]
            except Exception as e:
                msg = f'Error initializing Vectors: {str(e)}'
                logging.critical(msg)
                assert False, msg
            self.vs = vs_  # pyright: ignore[reportGeneralTypeIssues]

        # initialize from tuple or list of Vectors
        elif isinstance(vs_, (tuple, list)) and isinstance(vs_[0], Vectors):
            try:
                vs_ = np.stack([v.vs.squeeze() for v in vs_])  # pyright: ignore[reportGeneralTypeIssues]
            except Exception as e:
                msg = f'Error initializing Vectors: {str(e)}'
                logging.critical(msg)
                assert False, msg
            self.vs = vs_

        # initialize from single Vectors
        elif isinstance(vs_, Vectors):
            self.vs =  vs_.vs

        else:
            msg = 'Vectors must be constructed from Vectors, ndarray, or Tuples/List of floats/ints or Vectors'
            logging.critical(msg)
            assert False, msg

    def norm(self) -> None:
        ns: npt.NDArray[np.float64] = np.linalg.norm(self.vs, axis=-1)

        if np.min(ns) < TOLERANCE:
            logging.info(f"Encountered values close to zero in vector norm. Replacing with {TOLERANCE}")
            ns[ns < TOLERANCE] = TOLERANCE

        self.vs = self.vs / np.expand_dims(ns, axis=-1)

    def cross(self, v2: Vectors) -> Vectors:
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

    def perpendicular(self, ccw: bool = True) -> Vectors:
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

    def copy(self) -> Vectors:
        return copy(self)

    @property
    def shape(self) -> Tuple[int, ...]:
        return self.vs.shape

    @property
    def length(self) -> npt.NDArray[np.float32]:
        return np.linalg.norm(self.vs, axis=-1).astype(np.float32)

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

    def __copy__(self) -> Vectors:
        return Vectors(self)

    def __str__(self) -> str:
        return f"Vectors({str(self.vs)})"

    def __repr__(self) -> str:
        return f"Vectors({str(self.vs)})"
