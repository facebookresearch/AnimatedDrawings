import numpy as np
from model.arap import ARAP, plot_mesh
from model.old_arap import old_ARAP


def test_single_triangle_mesh():
    vertices = np.array([
        [2.0, 2.0],
        [3.0, 3.0],
        [4.0, 2.0]
    ])

    triangles = np.array([
        [0, 1, 2]
    ], np.int32)

    pins_xy = np.array([[2.2, 2.1], [3.6, 2.2]])
    plot_mesh(vertices, triangles, pins_xy)
    arap = ARAP(pins_xy, triangles=triangles, vertices=vertices)
    old = old_ARAP(pins_xy, triangles=triangles, vertices=vertices)

    pins_xy = np.array([[-5.0, 0.0], [6.0, 1.0]])
    v1, v2 = arap.solve(pins_xy)
    plot_mesh(v1.reshape([-1, 2]), triangles, pins_xy)
    plot_mesh(v2, triangles, pins_xy)

    pins_xy = np.array([[-5.0, 0.0], [6.0, 1.0]])
    v1, v2 = old._arap_solve(pins_xy)
    plot_mesh(v1.reshape([-1, 2]), triangles, pins_xy)
    plot_mesh(v2, triangles, pins_xy)

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

    pins_xy = np.array([[1.0, 0.0], [2.0, 0.0]])
    new = ARAP(pins_xy, triangles=triangles, vertices=vertices)
    old = old_ARAP(pins_xy, triangles=triangles, vertices=vertices)
    plot_mesh(vertices, triangles, pins_xy)

    pins_xy = np.array([[1.0, 0.0], [1.7, 0.7]])
    v1, v2 = new.solve(pins_xy)
    plot_mesh(v1.reshape([-1, 2]), triangles, pins_xy)
    plot_mesh(v2, triangles, pins_xy)


    pins_xy = np.array([[1.0, 0.0], [1.7, 0.7]])
    v1, v2 = old._arap_solve(pins_xy)
    plot_mesh(v1.reshape([-1, 2]), triangles, pins_xy)
    plot_mesh(v2, triangles, pins_xy)

    assert np.isclose(v2, np.array([
        [3.00000000e+00, 0.000000000e+00],
        [3.40000000+00, 1.000000000e+00],
        [4.800000004e+00, 1.000000000e+00],
        [5.99999657e+00, 0.00000000e-22]
    ])).all()

def test_four_triangle_mesh():
    vertices = np.array([
        [0.0, 0.0],
        [0.0, 1.0],
        [1.0, 1.0],
        [1.0, 0.0],
        [2.0, 1.0],
        [2.0, 0.0],
        [0.0, 2.0],
        [1.0, 2.0],
        [2.0, 2.0],
    ])

    triangles = np.array([
        [0, 1, 2],
        [0, 2, 3],
        [3, 2, 4],
        [3, 4, 5],

        [1, 6, 7],
        [1, 7, 2],
        [2, 7, 8],
        [2, 8, 4]
    ], np.int32)

    pins_xy = np.array([[0.0, 0.0], [0.0, 2.0], [2.0, 0.0]])
    new_pins_xy = np.array([[0.0, 0.0], [0.0, 2.0], [4.0, 0.0]])
    plot_mesh(vertices, triangles, pins_xy)
    new = ARAP(pins_xy, triangles=triangles, vertices=vertices)
    v1, v2 = new.solve(new_pins_xy)
    plot_mesh(v1.reshape([-1, 2]), triangles, new_pins_xy)
    plot_mesh(v2, triangles, new_pins_xy)

    plot_mesh(vertices, triangles, pins_xy)
    old = old_ARAP(pins_xy, triangles=triangles, vertices=vertices)
    v1, v2 = old._arap_solve(new_pins_xy)
    plot_mesh(v1.reshape([-1, 2]), triangles, new_pins_xy)
    plot_mesh(v2, triangles, new_pins_xy)


    # assert np.isclose(v2, np.array([
    #     [3.00000000e+00, 0.000000000e+00],
    #     [3.40000000+00, 1.000000000e+00],
    #     [4.800000004e+00, 1.000000000e+00],
    #     [5.99999657e+00, 0.00000000e-22]
    # ])).all()
