from __future__ import annotations  # so we can refer to class Type inside class
import numpy as np
import logging
from typing import Union
from model.vectors import Vectors


class Quaternions:
    """
    Wrapper class around ndarray interpreted as one or more quaternions.
    When passing in existing Vectors, new Vectors object will share the underlying nparray, so be careful.
    Inspired by Daniel Holden's excellent Quaternions class.
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

    @classmethod
    def from_angle_axis(cls, angles: np.ndarray, axes: Vectors):
        axes.norm()
        angles = np.expand_dims(angles, axis=0)
        ss = np.sin(angles / 2.0)
        cs = np.cos(angles / 2.0)
        return Quaternions(np.concatenate([cs, axes.vs * ss], axis=-1))

    @classmethod
    def identity(cls, ret_shape):
        qs = np.broadcast_to(np.array([1.0, 0.0, 0.0, 0.0]), [*ret_shape, 4])
        return Quaternions(qs)

    def quaternion_to_rotation_matrix(self) -> np.ndarray:
        """
        From Ken Shoemake
        https://www.ljll.math.upmc.fr/~frey/papers/scientific%20visualisation/Shoemake%20K.,%20Quaternions.pdf
        :return: 4x4 rotation matrix representation of quaternions

        >>> angles = np.array([[np.pi / 2]])
        >>> axis = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        >>> q1 = Quaternions.from_angle_axis(angles, axis)
        >>> assert np.allclose(q1.quaternion_to_rotation_matrix(), np.array([ \
        [ 1.000000e+00,  0.000000e+00,  0.000000e+00,  0.000000e+00], \
        [ 0.000000e+00,  0.000000e+00, -1.000000e+00,  0.000000e+00], \
        [ 0.000000e+00,  1.000000e+00,  0.000000e+00,  0.000000e+00], \
        [ 0.000000e+00,  0.000000e+00,  0.000000e+00,  1.000000e+00]]))
        """
        w = self.qs[..., 0]
        x = self.qs[..., 1]
        y = self.qs[..., 2]
        z = self.qs[..., 3]

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

        return np.array([[r00, r01, r02, 0],
                         [r10, r11, r12, 0],
                         [r20, r21, r22, 0],
                         [  0,   0,   0, 1]], dtype=np.float32)

    def normalize(self):
        self.qs = self.qs / np.expand_dims(np.sum(self.qs ** 2.0, axis=-1) ** 0.5, axis=-1)

    def __mul__(self, other: Quaternions) -> Quaternions:
        """
        From https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html
        :param other: Quaternion
        :return:
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

    @classmethod
    def from_euler_angles(cls, order: str, angles: np.ndarray):
        """

        :param order: string comprised of x, y, or z
        :param angles: angles in degrees
        :return:
        """
        assert len(order) == angles.shape[-1], 'length of orders and angles doesn\'t match'

        ret_q = Quaternions.identity(angles.shape[:-1])
        for axis_char, pos in zip(order, range(len(order))):
            angle = angles[..., pos] * np.pi / 180
            axis_char = axis_char.lower()

            assert axis_char in 'xyz', f'order contained unsupported char {axis_char}'

            axis = np.zeros([3])
            axis[ord(axis_char) - ord('x')] = 1.0

            ret_q *= Quaternions.from_angle_axis(angle, Vectors(axis))

        return ret_q


if __name__ == "__main__":
    # import doctest
    # doctest.testmod()
    # tests
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

    # Unit test: quaternion_to_rotation_matrix
    angles = np.array([[np.pi / 2]])
    axis = Vectors(np.array([1.0, 0.0, 0.0], dtype=np.float32))
    q1 = Quaternions.from_angle_axis(angles, axis)
    assert np.allclose(q1.quaternion_to_rotation_matrix(), np.array([
        [1.000000e+00,  0.000000e+00,  0.000000e+00,  0.000000e+00],
        [0.000000e+00,  0.000000e+00, -1.000000e+00,  0.000000e+00],
        [0.000000e+00,  1.000000e+00,  0.000000e+00,  0.000000e+00],
        [0.000000e+00,  0.000000e+00,  0.000000e+00,  1.000000e+00]]))

    # TODO add test coverage for from_euler_angles
