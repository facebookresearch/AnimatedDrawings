# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from animated_drawings.model.transform import Transform
from animated_drawings.model.quaternions import Quaternions
import numpy as np


def test_init():
    t = Transform()
    for m in [t._rotate_m, t._translate_m, t._scale_m, t._local_transform, t._world_transform]:
        assert np.array_equal(m, np.identity(4))


def test_set_position():
    t = Transform()
    t.set_position(np.array([1.0, 1.0, 1.0]))
    t.set_position(np.array([2.0, 2.0, 2.0]))
    t.update_transforms()
    assert np.array_equal(
        t._local_transform[:-1, -1], np.array([2.0, 2.0, 2.0]))


def test_offset():
    t = Transform()
    t.offset(np.array([1.0, 1.0, 1.0]))
    t.offset(np.array([2.0, 2.0, 2.0]))
    t.update_transforms()
    assert np.array_equal(
        t._local_transform[:-1, -1], np.array([3.0, 3.0, 3.0]))


def test_update_transforms():
    t1 = Transform()
    t2 = Transform()
    t1.add_child(t2)

    t1.set_position(np.array([3.0, 0.0, 0.0]))
    t1.update_transforms()
    assert np.array_equal(
        t2._world_transform[:-1, -1], np.array([3.0, 0.0, 0.0]))


def test_rotate():
    t = Transform()
    q = Quaternions.from_euler_angles('y', np.array([-90]))
    t.set_rotation(q)
    t.update_transforms()

    m = np.identity(4)
    m[0, 0] = 0.0
    m[2, 0] = 1.0
    m[2, 2] = 0.0
    m[0, 2] = -1.0

    assert np.isclose(t._local_transform, m).all()


def test_look_at():
    t = Transform()
    fwd = np.array([0, 0, -1])
    t.look_at(fwd)
    t.update_transforms()

    m = np.identity(4)
    m[0, 0] = -1.0
    m[2, 2] = -1.0
    assert np.isclose(t._local_transform, m).all()
