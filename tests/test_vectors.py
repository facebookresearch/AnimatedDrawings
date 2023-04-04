# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from animated_drawings.model.vectors import Vectors
import numpy as np


def test_initialize_with_tuple_or_list1():
    v1 = Vectors((0, 1, 2))
    assert np.array_equal(v1.vs, np.array([[0, 1, 2]]))

    v2 = Vectors([3, 4, 5])
    assert np.array_equal(v2.vs, np.array([[3, 4, 5]]))


def test_initialize2():
    try:
        Vectors('f')  # type: ignore
    except AssertionError:
        return
    assert False


def test_initialize_with_single_dimensional_array():
    v1 = Vectors(np.array([0, 1, 2]))
    assert np.array_equal(v1.vs, np.array([[0, 1, 2]]))


def test_div():
    v1 = Vectors(np.array([0, 1, 2]))
    assert np.array_equal((v1/2).vs, np.array([[0.0, 0.5, 1.0]]))


def test_norm():
    v1 = Vectors(np.array([10, 10, 10]))
    v1.norm()
    v2 = Vectors(np.array([10, 10, 10]) / 300**0.5)
    assert np.array_equal(v1.vs, v2.vs)


def test_norm_zero():
    v1 = Vectors(np.array([0, 0, 0]))
    v1.norm()
    v2 = Vectors(np.array([0, 0, 0]) / 1**0.5)
    assert np.array_equal(v1.vs, v2.vs)
