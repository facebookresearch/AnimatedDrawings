# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import numpy as np
from animated_drawings.model.arap import ARAP, plot_mesh


def test_single_triangle_mesh():
    show_plots = False  # Make true if you'd like to see mesh viz during test run
    vertices = np.array([
        [2.0, 2.0],
        [3.0, 3.0],
        [4.0, 2.0]
    ])

    triangles = np.array([
        [0, 1, 2]
    ], np.int32)

    pins_xy = np.array([[2.0, 2.0], [4.0, 2.0]])
    if show_plots:
        plot_mesh(vertices, triangles, pins_xy)
    arap = ARAP(pins_xy, triangles=triangles, vertices=vertices)

    pins_xy = np.array([[-5.0, 0.0], [5.0, 0.0]])
    v = arap.solve(pins_xy)
    if show_plots:
        plot_mesh(v, triangles, pins_xy)

    assert np.isclose(v, np.array([
        [-5.0, 0.0],
        [0.0, 1.0],
        [5.0, 0.0]
    ])).all()


def test_two_triangle_mesh():
    show_plots = False  # Make true if you'd like to see mesh viz during test run
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
    if show_plots:
        plot_mesh(vertices, triangles, pins_xy)

    pins_xy = np.array([[1.0, 0.0], [1.7, 0.7]])
    v = new.solve(pins_xy)
    if show_plots:
        plot_mesh(v, triangles, pins_xy)

    assert np.isclose(v, np.array([
        [9.99999989e-01, -1.13708135e-08],
        [2.91471856e-01,  7.05685418e-01],
        [9.97157285e-01,  1.41137085e+00],
        [1.70000001e+00,  7.00000011e-01]
    ])).all()


def test_four_triangle_mesh():
    show_plots = False  # Make true if you'd like to see mesh viz during test run
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
    if show_plots:
        plot_mesh(vertices, triangles, pins_xy)
    new = ARAP(pins_xy, triangles=triangles, vertices=vertices)

    new_pins_xy = np.array([[0.0, 0.0], [0.0, 3.0], [6.0, 0.0]])
    v = new.solve(new_pins_xy)
    if show_plots:
        plot_mesh(v, triangles, new_pins_xy)

    assert np.isclose(v, np.array([
        [3.19325865e-06, 1.08194488e-06],
        [6.78428061e-01, 1.37166545e+00],
        [2.14606263e+00, 1.19790398e+00],
        [2.81917351e+00, 1.12790606e-02],
        [3.95163838e+00, 1.34725960e+00],
        [5.99999596e+00, 5.51801260e-07],
        [8.44193478e-07, 2.99999837e+00],
        [1.46633111e+00, 2.60720416e+00],
        [2.82413859e+00, 2.62209072e+00]
    ])).all()
