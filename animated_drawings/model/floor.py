# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from animated_drawings.model.rectangle import Rectangle
from animated_drawings.model.transform import Transform
import numpy as np


class Floor(Transform):

    def __init__(self):
        super().__init__()

        for idx in range(-5, 5):
            for jdx in range(-5, 5):
                color = 'white' if (idx + jdx) % 2 else 'black'
                tile = Rectangle(color=color)
                tile.offset(np.array([float(idx), 0, float(jdx)]))
                self.add_child(tile)
