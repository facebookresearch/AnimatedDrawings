# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from animated_drawings.model.quaternions import Quaternions
from animated_drawings.model.vectors import Vectors
import numpy as np


def test_not_four_elements():
    try:
        Quaternions(np.array([0, 1, 2]))  # should fail
    except AssertionError:
        return
    assert False


def test_initialize_with_ndarray():
    q = Quaternions(np.array([1, 0, 0, 0]))  # should succeed
    assert np.array_equal(q.qs, np.array([[1, 0, 0, 0]]))


def test_from_angle_axis():
    angle = np.array([1.0])
    axis = Vectors(np.array([1.0, 1.0, 1.0]))
    q6 = Quaternions.from_angle_axis(angle, axis)
    assert np.allclose(q6.qs,  np.array(
        [[0.87758256, 0.27679646, 0.27679646, 0.27679646]]))


def test_multiple_from_angle_axis():
    angles = np.array([[1.0], [1.0]])
    axis = Vectors(
        np.array([[1.0, 1.0, 1.0], [1.0, 1.0, 1.0]], dtype=np.float32))
    q1 = Quaternions.from_angle_axis(angles, axis)
    assert np.allclose(q1.qs,  np.array([
        [0.87758256, 0.27679646, 0.27679646, 0.27679646],
        [0.87758256, 0.27679646, 0.27679646, 0.27679646]]))


def test_to_rotation_matrix():
    angles = np.array([[np.pi / 2]])
    axis = Vectors(np.array([1.0, 0.0, 0.0], dtype=np.float32))
    q1 = Quaternions.from_angle_axis(angles, axis)
    assert np.allclose(q1.to_rotation_matrix(), np.array([
        [1.000000e+00,  0.000000e+00,  0.000000e+00,  0.000000e+00],
        [0.000000e+00,  0.000000e+00, -1.000000e+00,  0.000000e+00],
        [0.000000e+00,  1.000000e+00,  0.000000e+00,  0.000000e+00],
        [0.000000e+00,  0.000000e+00,  0.000000e+00,  1.000000e+00]]))


def test_from_rotation_matrix():
    angles = np.array([[np.pi / 2]])
    axis = np.array([1.0, 1.0, 0.0], dtype=np.float32)
    q1 = Quaternions.from_angle_axis(angles, Vectors(axis))
    q2 = Quaternions.from_rotation_matrix(q1.to_rotation_matrix())
    assert np.allclose(q1.qs, q2.qs)


def test_to_euler_angles():
    # TODO add test coverage for from_euler_angles
    pass


def test_multiply():
    # TODO add test coverage for quaternion multiplication
    pass
