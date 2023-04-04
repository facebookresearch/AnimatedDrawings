# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import numpy as np
import numpy.typing as npt
import logging


def get_projection_matrix(buffer_w: int, buffer_h: int, type_: str = 'perspective') -> npt.NDArray[np.float32]:

    if type_ == 'perspective':

        fov = 35.0
        near = 0.1
        aspect = buffer_w / buffer_h
        top = near * np.tan(fov * np.pi / 360)
        right = top * aspect
        far = 10000.0
        bottom = -top
        left = -right

        M_0_0 =       (2 * near) / (right - left)
        M_0_2 =   (left + right) / (left - right)
        M_1_1 =       (2 * near) / (top - bottom)
        M_1_2 =   (bottom + top) / (bottom-top)
        M_2_2 =     (far + near) / (near - far)
        M_2_3 = (2 * far * near) / (near - far)
        M_3_2 = -1

        M: npt.NDArray[np.float32] = np.zeros([4, 4], dtype=np.float32)
        M[0, 0] = M_0_0
        M[0, 2] = M_0_2
        M[1, 1] = M_1_1
        M[1, 2] = M_1_2
        M[2, 2] = M_2_2
        M[2, 3] = M_2_3
        M[3, 2] = M_3_2
        return M

    else:
        logging.critical(f'unsupported camera type specified: {type_}')
        assert False
