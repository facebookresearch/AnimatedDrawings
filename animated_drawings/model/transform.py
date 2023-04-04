# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import annotations  # so we can refer to class Type inside class
import numpy as np
import numpy.typing as npt
from animated_drawings.model.vectors import Vectors
from animated_drawings.model.quaternions import Quaternions
import logging
from typing import Union, Optional, List, Tuple


class Transform():
    """Base class from which all other scene objects descend"""

    def __init__(self,
                 parent: Optional[Transform] = None,
                 name: Optional[str] = None,
                 children: List[Transform] = [],
                 offset: Union[npt.NDArray[np.float32], Vectors, None] = None,
                 **kwargs
                 ) -> None:

        super().__init__(**kwargs)

        self._parent: Optional[Transform] = parent

        self._children: List[Transform] = []
        for child in children:
            self.add_child(child)

        self.name: Optional[str] = name

        self._translate_m: npt.NDArray[np.float32] = np.identity(4, dtype=np.float32)
        self._rotate_m: npt.NDArray[np.float32] = np.identity(4, dtype=np.float32)
        self._scale_m: npt.NDArray[np.float32] = np.identity(4, dtype=np.float32)

        if offset is not None:
            self.offset(offset)

        self._local_transform: npt.NDArray[np.float32] = np.identity(4, dtype=np.float32)
        self._world_transform: npt.NDArray[np.float32] = np.identity(4, dtype=np.float32)
        self.dirty_bit: bool = True  # are world/local transforms stale?

    def update_transforms(self, parent_dirty_bit: bool = False, recurse_on_children: bool = True, update_ancestors: bool = False) -> None:
        """
        Updates transforms if stale.
        If own dirty bit is set, recompute local matrix
        If own or parent's dirty bit is set, recompute world matrix
        If own or parent's dirty bit is set, recurses on children, unless param recurse_on_children is false.
        If update_ancestors is true, first find first ancestor, then call update_transforms upon it.
        Set dirty bit back to false.
        """
        if update_ancestors:
            ancestor, ancestor_parent = self, self.get_parent()
            while ancestor_parent is not None:
                ancestor, ancestor_parent = ancestor_parent, ancestor_parent.get_parent()
            ancestor.update_transforms()

        if self.dirty_bit:
            self.compute_local_transform()
        if self.dirty_bit | parent_dirty_bit:
            self.compute_world_transform()

        if recurse_on_children:
            for c in self.get_children():
                c.update_transforms(self.dirty_bit | parent_dirty_bit)

        self.dirty_bit = False

    def compute_local_transform(self) -> None:
        self._local_transform = self._translate_m @ self._rotate_m @ self._scale_m

    def compute_world_transform(self) -> None:
        self._world_transform = self._local_transform
        if self._parent:
            self._world_transform = self._parent._world_transform @ self._world_transform

    def get_world_transform(self, update_ancestors: bool = True) -> npt.NDArray[np.float32]:
        """
        Get the transform's world matrix.
        If update is true, check to ensure the world_transform is current
        """
        if update_ancestors:
            self.update_transforms(update_ancestors=True)
        return np.copy(self._world_transform)

    def set_scale(self, scale: float) -> None:
        self._scale_m[:-1, :-1] = scale * np.identity(3, dtype=np.float32)
        self.dirty_bit = True

    def set_position(self, pos: Union[npt.NDArray[np.float32], Vectors]) -> None:
        """ Set the absolute values of the translational elements of transform """
        if isinstance(pos, Vectors):
            pos = pos.vs

        if pos.shape == (1, 3):
            pos = np.squeeze(pos)
        elif pos.shape == (3,):
            pass
        else:
            msg = f'bad vector dim passed to set_position. Found: {pos.shape}'
            logging.critical(msg)
            assert False, msg

        self._translate_m[:-1, -1] = pos
        self.dirty_bit = True

    def get_local_position(self) -> npt.NDArray[np.float32]:
        """ Ensure local transform is up-to-date and return local xyz coordinates """
        if self.dirty_bit:
            self.compute_local_transform()
        return np.copy(self._local_transform[:-1, -1])

    def get_world_position(self, update_ancestors: bool = True) -> npt.NDArray[np.float32]:
        """
        Ensure all parent transforms are update and return world xyz coordinates
        If update_ancestor_transforms is true, update ancestor transforms to ensure
        up-to-date world_transform before returning
        """
        if update_ancestors:
            self.update_transforms(update_ancestors=True)

        return np.copy(self._world_transform[:-1, -1])

    def offset(self, pos: Union[npt.NDArray[np.float32], Vectors]) -> None:
        """ Translational offset by the specified amount """

        if isinstance(pos, Vectors):
            pos = pos.vs[0]
        assert isinstance(pos, np.ndarray)

        self.set_position(self._translate_m[:-1, -1] + pos)

    def look_at(self, fwd_: Union[npt.NDArray[np.float32], Vectors, None]) -> None:
        """Given a forward vector, rotate the transform to face that position"""
        if fwd_ is None:
            fwd_ = Vectors(self.get_world_position())
        elif isinstance(fwd_, np.ndarray):
            fwd_ = Vectors(fwd_)
        fwd: Vectors = fwd_.copy()  # norming will change the vector

        if fwd.vs.shape != (1, 3):
            msg = f'look_at fwd_ vector must have shape [1,3]. Found: {fwd.vs.shape}'
            logging.critical(msg)
            assert False, msg

        tmp: Vectors = Vectors([0.0, 1.0, 0.0])

        # if fwd and tmp are same vector, modify tmp to avoid collapse
        if np.isclose(fwd.vs, tmp.vs).all() or np.isclose(fwd.vs, -tmp.vs).all():
            tmp.vs[0] += 0.001

        right: Vectors = tmp.cross(fwd)
        up: Vectors = fwd.cross(right)

        fwd.norm()
        right.norm()
        up.norm()

        rotate_m = np.identity(4, dtype=np.float32)
        rotate_m[:-1, 0] = np.squeeze(right.vs)
        rotate_m[:-1, 1] = np.squeeze(up.vs)
        rotate_m[:-1, 2] = np.squeeze(fwd.vs)

        self._rotate_m = rotate_m
        self.dirty_bit = True

    def get_right_up_fwd_vectors(self) -> Tuple[npt.NDArray[np.float32], npt.NDArray[np.float32], npt.NDArray[np.float32]]:
        inverted: npt.NDArray[np.float32] = np.linalg.inv(self.get_world_transform())
        right: npt.NDArray[np.float32] = inverted[:-1, 0]
        up: npt.NDArray[np.float32] = inverted[:-1, 1]
        fwd: npt.NDArray[np.float32] = inverted[:-1, 2]

        return right, up, fwd

    def set_rotation(self, q: Quaternions) -> None:
        if q.qs.shape != (1, 4):
            msg = f'set_rotate q must have dimension (1, 4). Found: {q.qs.shape}'
            logging.critical(msg)
            assert False, msg
        self._rotate_m = q.to_rotation_matrix()
        self.dirty_bit = True

    def rotation_offset(self, q: Quaternions) -> None:
        if q.qs.shape != (1, 4):
            msg = f'set_rotate q must have dimension (1, 4). Found: {q.qs.shape}'
            logging.critical(msg)
            assert False, msg
        self._rotate_m = (q * Quaternions.from_rotation_matrix(self._rotate_m)).to_rotation_matrix()
        self.dirty_bit = True

    def add_child(self, child: Transform) -> None:
        self._children.append(child)
        child.set_parent(self)

    def get_children(self) -> List[Transform]:
        return self._children

    def set_parent(self, parent: Transform) -> None:
        self._parent = parent
        self.dirty_bit = True

    def get_parent(self) -> Optional[Transform]:
        return self._parent

    def get_transform_by_name(self, name: str) -> Optional[Transform]:
        """ Search self and children for transform with matching name. Return it if found, None otherwise. """

        # are we match?
        if self.name == name:
            return self

        # recurse to check if a child is match
        for c in self.get_children():
            transform_or_none = c.get_transform_by_name(name)
            if transform_or_none:  # if we found it
                return transform_or_none

        # no match
        return None

    def draw(self, recurse: bool = True, **kwargs) -> None:
        """ Draw this transform and recurse on children """
        self._draw(**kwargs)

        if recurse:
            for child in self.get_children():
                child.draw(**kwargs)

    def _draw(self, **kwargs) -> None:
        """Transforms default to not being drawn. Subclasses must implement how they appear"""
