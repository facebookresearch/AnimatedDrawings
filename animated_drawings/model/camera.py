# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from animated_drawings.model.transform import Transform
from animated_drawings.model.vectors import Vectors
from typing import Union, List


class Camera(Transform):

    def __init__(
        self,
        pos: Union[Vectors, List[Union[float, int]]] = Vectors([0.0, 0.0, 0.0]),
        fwd: Union[Vectors, List[Union[float, int]]] = Vectors([0.0, 0.0, 1.0])
    ):
        super().__init__()

        if not isinstance(pos, Vectors):
            pos = Vectors(pos)
        self.set_position(pos)

        if not isinstance(fwd, Vectors):
            fwd = Vectors(fwd)
        self.look_at(fwd)
