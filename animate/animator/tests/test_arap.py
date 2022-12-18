import numpy as np
from model.arap import ARAP


def test_single_triangle_mesh():
    vertices = np.array([
    [0.0, 0.0],
    [1.0, 1.0],
    [2.0, 0.0]
    ])

    triangles = np.array([
        [0, 1, 2]
    ],np.int32)

    pin_v_idxs = np.array([0, 2])
    arap = ARAP(pin_v_idxs, triangles=triangles, vertices=vertices)
    v2 = arap.solve([[0, 0], [0, -4]])

    assert np.isclose(v2, np.array([
    [0.00000000e+00, -2.99999100e-06],
    [1.00000000e+00, -2.00000000e+00],
    [6.93003543e-23, -3.99999700e+00]
    ])).all()


def test_two_triangle_mesh():
    vertices = np.array([
    [1.0, 0.0],
    [1.0, 1.0],
    [2.0, 1.0],
    [2.0, 0.0],
    ])

    triangles = np.array([
        [0, 1, 2],
        [0, 2, 3],
    ],np.int32)

    pin_v_idxs = np.array([0, 3])
    new = ARAP(pin_v_idxs, triangles=triangles, vertices=vertices)
    v2 = new.solve([[3, 0], [6, 0]])
    assert np.isclose(v2, np.array([
        [3.00000000e+00, 0.000000000e+00],
        [3.28571673e+00, 1.000000000e+00],
        [4.57143004e+00, 1.000000000e+00],
        [5.99999657e+00, 0.00000000e-22]
        ])).all()