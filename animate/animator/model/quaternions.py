from __future__ import annotations  # so we can refer to class Type inside class
import numpy as np
import logging
from typing import Union
from model.vectors import Vectors
import math
from utils import tolerance
from functools import reduce


class Quaternions:
    """
    Wrapper class around ndarray interpreted as one or more quaternions. Quaternion order is [w, x, y, z]
    When passing in existing Quaternions, new Quaternions object will share the underlying nparray, so be careful.
    Strongly influenced by Daniel Holden's excellent Quaternions class.
    """

    def __init__(self, qs: Union[tuple, list, np.ndarray, Quaternions]):
        if isinstance(qs, np.ndarray):
            if not qs.shape[-1] == 4:
                msg = f'Final dimension passed to Quaternions must be 4. Found {qs.shape[-1]}'
                logging.critical(msg)
                assert False, msg

            if len(qs.shape) == 1:
                qs = np.expand_dims(qs, axis=0)

            self.qs = qs

        elif isinstance(qs, tuple) or isinstance(qs, list):
            try:
                qs = np.array(qs)
                assert qs.shape[-1] == 4
            except Exception:
                msg = 'Could not convert quaternion data to ndarray with shape[-1] == 4'
                logging.critical(msg)
                assert False, msg

            self.qs = qs

        elif isinstance(qs, Quaternions):
            self.qs = qs.qs

        else:
            msg = 'Quaternions must be constructed from Quaternions or numpy array'
            logging.critical(msg)
            assert False, msg

        self.normalize()

    def normalize(self) -> None:
        self.qs = self.qs / np.expand_dims(np.sum(self.qs ** 2.0, axis=-1) ** 0.5, axis=-1)

    def to_rotation_matrix(self) -> np.ndarray:
        """
        From Ken Shoemake
        https://www.ljll.math.upmc.fr/~frey/papers/scientific%20visualisation/Shoemake%20K.,%20Quaternions.pdf
        :return: 4x4 rotation matrix representation of quaternions
        """
        w = self.qs[..., 0].squeeze()
        x = self.qs[..., 1].squeeze()
        y = self.qs[..., 2].squeeze()
        z = self.qs[..., 3].squeeze()

        xx, yy, zz = x**2, y**2, z**2

        wx, wy, wz = w*x, w*y, w*z
        xy, xz     = x*y, x*z  # no
        yz         = y*z

        # Row 1
        r00 = 1 - 2 * (yy + zz)
        r01 = 2 * (xy - wz)
        r02 = 2 * (xz + wy)

        # Row 2
        r10 = 2 * (xy + wz)
        r11 = 1 - 2 * (xx + zz)
        r12 = 2 * (yz - wx)

        # Row 3
        r20 = 2 * (xz - wy)
        r21 = 2 * (yz + wx)
        r22 = 1 - 2 * (xx + yy)

        return np.array([[r00, r01, r02, 0.0],
                         [r10, r11, r12, 0.0],
                         [r20, r21, r22, 0.0],
                         [0.0, 0.0, 0.0, 1.0]], dtype=np.float32)

    @classmethod
    def from_angle_axis(cls, angles: np.ndarray, axes: Vectors) -> Quaternions:
        axes.norm()

        if len(angles.shape) == 1:
            angles = np.expand_dims(angles, axis=0)

        ss = np.sin(angles / 2.0)
        cs = np.cos(angles / 2.0)
        return Quaternions(np.concatenate([cs, axes.vs * ss], axis=-1))

    @classmethod
    def identity(cls, ret_shape) -> Quaternions:
        qs = np.broadcast_to(np.array([1.0, 0.0, 0.0, 0.0]), [*ret_shape, 4])
        return Quaternions(qs)

    @classmethod
    def from_euler_angles(cls, order: str, angles: np.ndarray) -> Quaternions:
        """
        :param order: string comprised of x, y, and/or z
        :param angles: angles in degrees
        """
        if len(angles.shape) == 1:
            angles = np.expand_dims(angles, axis=0)

        if len(order) != angles.shape[-1]:
            msg = 'lengh of orders and angles does not match'
            logging.critical(msg)
            assert False, msg

        _quats = [Quaternions.identity(angles.shape[:-1])]
        for axis_char, pos in zip(order, range(len(order))):

            angle = angles[..., pos] * np.pi / 180
            angle = np.expand_dims(angle, axis=1)

            axis_char = axis_char.lower()
            if axis_char not in 'xyz':
                msg = f'order contained unsupported char:{axis_char}'
                logging.critical(msg)
                assert False, msg

            axis = np.zeros([*angles.shape[:-1], 3])
            axis[...,ord(axis_char) - ord('x')] = 1.0

            _quats.insert(0, Quaternions.from_angle_axis(angle, Vectors(axis)))

        ret_q = reduce(lambda a, b: b * a, _quats)
        return ret_q

    @classmethod
    def from_rotation_matrix(cls, M: np.ndarray) -> Quaternions:
        """
        As described here: https://d3cw3dd2w32x2b.cloudfront.net/wp-content/uploads/2015/01/matrix-to-quat.pdf
        """
        is_orthogonal = np.isclose(M @ M.T, np.identity(4), atol=tolerance)
        if not is_orthogonal.all():
            msg = "attempted to create quaternion from non-orthogonal rotation matrix"
            logging.critical(msg)
            assert False, msg

        if not np.isclose(np.linalg.det(M), 1.0):
            msg = "attempted to create quaternion from rotation matrix with det != 1"
            logging.critical(msg)
            assert False, msg

        # Note: Mike Day's article uses row vectors, whereas we used column, so here use transpose of matrix
        MT = M.T
        m00, m01, m02 = MT[0,0], MT[0,1], MT[0,2]
        m10, m11, m12 = MT[1,0], MT[1,1], MT[1,2]
        m20, m21, m22 = MT[2,0], MT[2,1], MT[2,2]

        if m22 < 0:
            if m00 > m11:
                t = 1 + m00 - m11 - m22
                q = np.array([m12-m21,      t, m01+m10, m20+m02,])
            else:
                t = 1 - m00 + m11 - m22
                q = np.array([m20-m02, m01+m10,       t, m12+m21])
        else:
            if m00 < -m11:
                t = 1 - m00 - m11 + m22
                q = np.array([m01-m10, m20+m02, m12+m21,       t])
            else:
                t = 1 + m00 + m11 + m22
                q = np.array([      t, m12-m21, m20-m02, m01-m10])

        q *= (0.5 / math.sqrt(t))

        ret_q = Quaternions(q)
        ret_q.normalize()
        return ret_q

    def __mul__(self, other: Quaternions):
        """
        From https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html
        """
        s0 = self.qs[..., 0]
        s1 = self.qs[..., 1]
        s2 = self.qs[..., 2]
        s3 = self.qs[..., 3]

        r0 = other.qs[..., 0]
        r1 = other.qs[..., 1]
        r2 = other.qs[..., 2]
        r3 = other.qs[..., 3]

        t = np.empty(self.qs.shape)

        t[..., 0] = r0*s0 - r1*s1 - r2*s2 - r3*s3
        t[..., 1] = r0*s1 + r1*s0 - r2*s3 + r3*s2
        t[..., 2] = r0*s2 + r1*s3 + r2*s0 - r3*s1
        t[..., 3] = r0*s3 - r1*s2 + r2*s1 + r3*s0

        return Quaternions(t)

    def __neg__(self):
        return Quaternions(self.qs * np.array([1, -1, -1, -1]))

    def __str__(self):
        return f"Quaternions({str(self.qs)})"

    def __repr__(self):
        return f"Quaternions({str(self.qs)})"


if __name__ == "__main__":
    # TODO: Move these to dedicated testing file
    try:
        q1 = Quaternions(np.array([0, 1, 2]))  # should fail
    except Exception:
        print('failed test. okay')
        pass
    try:
        q2 = Quaternions(np.array([0, 1, 2]))  # should fail
    except Exception:
        print('failed test. okay')
        pass
    q3 = Quaternions(np.array([0, 1, 2, 3]))  # should succeed
    q4 = Quaternions(np.array([[0, 1, 2, 3]]))  # should succeed
    q5 = Quaternions(q4)  # should succeed

    angle = np.array([1.0])
    axis = Vectors(np.array([1.0, 1.0, 1.0]))
    q6 = Quaternions.from_angle_axis(angle, axis)

    assert np.allclose(q6.qs,  np.array([[0.87758256, 0.27679646, 0.27679646, 0.27679646]]))

    # Unit test: multiple angles and axes
    angles = np.array([[1.0], [1.0]])
    axis = Vectors(np.array([[1.0, 1.0, 1.0], [1.0, 1.0, 1.0]], dtype=np.float32))
    q1 = Quaternions.from_angle_axis(angles, axis)
    assert np.allclose(q1.qs,  np.array([
        [0.87758256, 0.27679646, 0.27679646, 0.27679646],
        [0.87758256, 0.27679646, 0.27679646, 0.27679646]]))

    # Unit test: to_rotation_matrix
    angles = np.array([[np.pi / 2]])
    axis = Vectors(np.array([1.0, 0.0, 0.0], dtype=np.float32))
    q1 = Quaternions.from_angle_axis(angles, axis)
    assert np.allclose(q1.to_rotation_matrix(), np.array([
        [1.000000e+00,  0.000000e+00,  0.000000e+00,  0.000000e+00],
        [0.000000e+00,  0.000000e+00, -1.000000e+00,  0.000000e+00],
        [0.000000e+00,  1.000000e+00,  0.000000e+00,  0.000000e+00],
        [0.000000e+00,  0.000000e+00,  0.000000e+00,  1.000000e+00]]))

    # TODO add test coverage for from_euler_angles

    # unit test from_rotation_matrix:
    M = np.identity(4)
    M[2, 2] = 0
    M[0, 2] = 1
    M[0, 0] = 0
    M[2, 0] = -1
    assert np.allclose(M, Quaternions.from_rotation_matrix(M).to_rotation_matrix())

    angles = np.array([[np.pi / 2]])
    axis = np.array([1.0, 1.0, 0.0], dtype=np.float32)
    q1 = Quaternions.from_angle_axis(angles, Vectors(axis))
    assert np.allclose(q1.qs, Quaternions.from_rotation_matrix(q1.to_rotation_matrix()).qs)
