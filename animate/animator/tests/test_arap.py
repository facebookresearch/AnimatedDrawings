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
    ], np.int32)

    pin_locs = np.array([[0.0, 0.0], [2.0, 0.0]])
    arap = ARAP(pin_locs, triangles=triangles, vertices=vertices)
    pin_locs = np.array([[0.0, 0.0], [0.0, -4.0]])
    v2 = arap.solve(pin_locs)

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
    ], np.int32)

    pin_locs = np.array([[1.0, 0.0], [2.0, 0.0]])
    new = ARAP(pin_locs, triangles=triangles, vertices=vertices)
    pin_locs = np.array([[3.0, 0.0], [6.0, 0.0]])
    v2 = new.solve(pin_locs)
    assert np.isclose(v2, np.array([
        [3.00000000e+00, 0.000000000e+00],
        [3.40000000+00, 1.000000000e+00],
        [4.800000004e+00, 1.000000000e+00],
        [5.99999657e+00, 0.00000000e-22]
    ])).all()
