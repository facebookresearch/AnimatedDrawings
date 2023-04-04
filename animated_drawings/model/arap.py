# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import numpy as np
import numpy.typing as npt
from collections import defaultdict
import logging
from typing import List, Dict, Set, Tuple
import scipy.sparse.linalg as spla
import scipy.sparse as sp


csr_matrix = sp._csr.csr_matrix  # for typing  # pyright: ignore[reportPrivateUsage]


class ARAP():
    """
    Implementation of:

    Takeo Igarashi and Yuki Igarashi.
    "Implementing As-Rigid-As-Possible Shape Manipulation and Surface Flattening."
    Journal of Graphics, GPU, and Game Tools, A.K.Peters, Volume 14, Number 1, pp.17-30, ISSN:2151-237X, June, 2009.
    https://www-ui.is.s.u-tokyo.ac.jp/~takeo/papers/takeo_jgt09_arapFlattening.pdf

    General idea is this:
    Start with an an input mesh, comprised of vertices (v in V) and edges (e in E),
    and an initial set of pins (or control handle) locations.

    Then, given new positions for the pins, find new vertex locations (v' in V')
    such that the edges (e' in E') are as similar as possible, in a least squares sense, to the original edges (e in E).
    Translation and rotation aren't penalized, but edge scaling is.
    Not allowing rotation makes this tricky, as edges are directed vectors.

    Solution involves finding vertex locations twice. First, you do so while allowing both rotation and scaling to be free.
    Then you collect the per-edge rotation transforms found by this solution.
    During the second solve, you rotate the original edges (e in E) by the rotation matrix prior to computing the difference
    between (e' in E') and (e in E). This way, rotation is essentially free, while scaling is not.
    """

    def __init__(self, pins_xy: npt.NDArray[np.float32], triangles: List[npt.NDArray[np.int32]], vertices: npt.NDArray[np.float32], w: int = 1000):  # noqa: C901
        """
        Sets up the matrices needed for later solves.

        pins_xy: ndarray [N, 2] specifying initial xy positions of N control points
        vertices: ndarray [N, 2] containing xy positions of N vertices. A vertex's order within array is it's vertex ID
        triangles: ndarray [N, 3] triplets of vertex IDs that make up triangles comprising the mesh
        w: int the weights to use for control points in solve. Default value should work.
        """
        self.w = w

        self.vertices = np.copy(vertices)

        # build a deduplicated list of edge->vertex IDS...
        self.e_v_idxs: List[Tuple[np.int32, np.int32]] = []
        for v0, v1, v2 in triangles:
            self.e_v_idxs.append(tuple(sorted((v0, v1))))
            self.e_v_idxs.append(tuple(sorted((v1, v2))))
            self.e_v_idxs.append(tuple(sorted((v2, v0))))
        self.e_v_idxs = list(set(self.e_v_idxs))  # ...and deduplicate it

        # build list of edge vectors
        _edge_vectors: List[npt.NDArray[np.float32]] = []
        for vi_idx, vj_idx in self.e_v_idxs:
            vi = self.vertices[vi_idx]
            vj = self.vertices[vj_idx]
            _edge_vectors.append(vj - vi)
        self.edge_vectors: npt.NDArray[np.float32] = np.array(_edge_vectors)

        # get barycentric coordinates of pins, and mask denoting which pins were initially outside the mesh
        pins_bc: List[Tuple[Tuple[np.int32, np.float32], Tuple[np.int32, np.float32], Tuple[np.int32, np.float32]]]
        self.pin_mask = npt.NDArray[np.bool8]
        pins_bc, self.pin_mask = self._xy_to_barycentric_coords(pins_xy, vertices, triangles)

        v_vnbr_idxs: Dict[np.int32, Set[np.int32]] = defaultdict(set)  # build a dict mapping vertex ID -> neighbor vertex IDs
        for v0, v1, v2 in triangles:
            v_vnbr_idxs[v0] |= {v1, v2}
            v_vnbr_idxs[v1] |= {v2, v0}
            v_vnbr_idxs[v2] |= {v0, v1}

        self.edge_num = len(self.e_v_idxs)
        self.vert_num = len(self.vertices)
        self.pin_num = len(pins_xy[self.pin_mask])

        self.A1: npt.NDArray[np.float32] = np.zeros([2 * (self.edge_num + self.pin_num), 2 * self.vert_num], dtype=np.float32)
        G: npt.NDArray[np.float32] = np.zeros([2 * self.edge_num, 2 * self.vert_num], dtype=np.float32)  # holds edge rotation calculations

        # populate top half of A1, one row per edge
        for k, (vi_idx, vj_idx) in enumerate(self.e_v_idxs):

            # initialize self.A1 with 1, -1 denoting beginning and end of x and y dims of vector
            self.A1[2*k:2*(k+1), 2*vi_idx:2*(vi_idx+1)] = -np.identity(2)
            self.A1[2*k:2*(k+1), 2*vj_idx:2*(vj_idx+1)] = np.identity(2)

            # Find the 'neighbor' vertices for this edge: {v_i, v_j,v_r, v_l}
            vi_vnbr_idxs: Set[np.int32] = v_vnbr_idxs[vi_idx]
            vj_vnbr_idxs: Set[np.int32] = v_vnbr_idxs[vj_idx]
            e_vnbr_idxs: List[np.int32] = list(vi_vnbr_idxs.intersection(vj_vnbr_idxs))
            e_vnbr_idxs.insert(0, vi_idx)
            e_vnbr_idxs.insert(1, vj_idx)

            e_vnbr_xys: Tuple[np.float32, np.float32] = tuple([self.vertices[v_idx] for v_idx in e_vnbr_idxs])

            _: List[Tuple[float, float]] = []
            for v in e_vnbr_xys[1:]:
                vx: float = v[0] - e_vnbr_xys[0][0]
                vy: float = v[1] - e_vnbr_xys[0][1]
                _.extend(((vx, vy), (vy, -vx)))
            G_k: npt.NDArray[np.float32] = np.array(_)

            G_k_star: npt.NDArray[np.float32] = np.linalg.inv(G_k.T @ G_k) @ G_k.T

            e_kx, e_ky = self.edge_vectors[k]
            e = np.array([
                [e_kx,  e_ky],
                [e_ky, -e_kx]
            ], np.float32)

            edge_matrix = np.hstack([np.tile(-np.identity(2), (len(e_vnbr_idxs)-1, 1)), np.identity(2*(len(e_vnbr_idxs)-1))])
            g = np.dot(G_k_star, edge_matrix)
            h = np.dot(e, g)

            for h_offset, v_idx in enumerate(e_vnbr_idxs):
                self.A1[2*k:2*(k+1), 2*v_idx:2*(v_idx+1)] -= h[:, 2*h_offset:2*(h_offset+1)]
                G[2*k:2*(k+1), 2*v_idx:2*(v_idx+1)] = g[:, 2*h_offset:2*(h_offset+1)]

        # populate bottom row of A1, one row per constraint-dimension
        for pin_idx, pin_bc in enumerate(pins_bc):
            for v_idx, v_w in pin_bc:
                self.A1[2*self.edge_num + 2*pin_idx  , 2*v_idx]     = self.w * v_w  # x component
                self.A1[2*self.edge_num + 2*pin_idx+1, 2*v_idx + 1] = self.w * v_w  # y component

        A2_top: npt.NDArray[np.float32] = np.zeros([self.edge_num, self.vert_num], dtype=np.float32)
        for k, (vi_idx, vj_idx) in enumerate(self.e_v_idxs):
            A2_top[k, vi_idx] = -1
            A2_top[k, vj_idx] = 1

        A2_bot: npt.NDArray[np.float32] = np.zeros([self.pin_num, self.vert_num], dtype=np.float32)
        for pin_idx, pin_bc in enumerate(pins_bc):
            for v_idx, v_w in pin_bc:
                A2_bot[pin_idx, v_idx] = self.w * v_w

        self.A2: npt.NDArray[np.float32] = np.vstack([A2_top, A2_bot])

        # for speed, convert to sparse matrices and cache for later
        self.tA1: csr_matrix = sp.csr_matrix(self.A1.transpose())
        self.tA2: csr_matrix = sp.csr_matrix(self.A2.transpose())
        self.G: csr_matrix = sp.csr_matrix(G)

        # perturbing singular matrix and calling det can trigger overflow warning- ignore it
        old_settings = np.seterr(over='ignore')

        # ensure tA1xA1 matrix isn't singular and cache sparse repsentation
        tA1xA1_dense: npt.NDArray[np.float32] = self.tA1 @ self.A1
        while np.linalg.det(tA1xA1_dense) == 0.0:
            logging.info('tA1xA1 is singular. perturbing...')
            tA1xA1_dense += 0.00000001 * np.identity(tA1xA1_dense.shape[0])
        self.tA1xA1: csr_matrix = sp.csr_matrix(tA1xA1_dense)

        # ensure tA2xA2 matrix isn't singular and cache sparse repsentation
        tA2xA2_dense: npt.NDArray[np.float32] = self.tA2 @ self.A2
        while np.linalg.det(tA2xA2_dense) == 0.0:
            logging.info('tA2xA2 is singular. perturbing...')
            tA2xA2_dense += 0.00000001 * np.identity(tA2xA2_dense.shape[0])
        self.tA2xA2: csr_matrix = sp.csr_matrix(tA2xA2_dense)

        # revert np overflow warnings behavior
        np.seterr(**old_settings)

    def solve(self, pins_xy_: npt.NDArray[np.float32]) -> npt.NDArray[np.float64]:
        """
        After ARAP has been initialized, pass in new pin xy positions and receive back the new mesh vertex positions
        pins *must* be in the same order they were passed in during initialization

        pins_xy: ndarray [N, 2] with new pin xy positions
        return: ndarray [N, 2], the updated xy locations of each vertex in the mesh
        """

        # remove any pins that were orgininally outside the mesh
        pins_xy: npt.NDArray[np.float32] = pins_xy_[self.pin_mask]  # pyright: ignore[reportGeneralTypeIssues]

        assert len(pins_xy) == self.pin_num

        self.b1: npt.NDArray[np.float64] = np.hstack([np.zeros([2 * self.edge_num], dtype=np.float64), self.w * pins_xy.reshape([-1, ])])
        v1: npt.NDArray[np.float64] = spla.spsolve(self.tA1xA1, self.tA1 @ self.b1.T)

        T1: npt.NDArray[np.float64] = self.G @ v1
        b2_top = np.empty([self.edge_num, 2], dtype=np.float64)
        for idx, e0 in enumerate(self.edge_vectors):
            c: np.float64 = T1[2*idx]
            s: np.float64 = T1[2*idx + 1]
            scale = 1.0 / np.sqrt(c * c + s * s)
            c *= scale
            s *= scale
            T2 = np.asarray(((c, s), (-s, c)))  # create rotation matrix
            e1 = np.dot(T2, e0)                 # and rotate old vector to get new
            b2_top[idx] = e1
        b2 = np.vstack([b2_top, self.w * pins_xy])
        b2x = b2[:, 0]
        b2y = b2[:, 1]

        v2x: npt.NDArray[np.float64] = spla.spsolve(self.tA2xA2, self.tA2 @ b2x)
        v2y: npt.NDArray[np.float64] = spla.spsolve(self.tA2xA2, self.tA2 @ b2y)

        return np.vstack((v2x, v2y)).T

    def _xy_to_barycentric_coords(self,
                                  points: npt.NDArray[np.float32],
                                  vertices: npt.NDArray[np.float32],
                                  triangles: List[npt.NDArray[np.int32]]
                                  ) -> Tuple[List[Tuple[Tuple[np.int32, np.float32], Tuple[np.int32, np.float32], Tuple[np.int32, np.float32]]],
                                             npt.NDArray[np.bool8]]:
        """
        Given and array containing xy locations and the vertices & triangles making up a mesh,
        find the triangle that each points in within and return it's representation using barycentric coordinates.
        points: ndarray [N,2] of point xy coords
        vertices: ndarray of vertex locations, row position is index id
        triangles: ndarraywith ordered vertex ids of vertices that make up each mesh triangle

        Is point inside triangle? : https://mathworld.wolfram.com/TriangleInterior.html

        Returns a list of barycentric coords for points inside the mesh,
        and a list of True/False values indicating whether a given pin was inside the mesh or not.
        Needed for removing pins during subsequent solve steps.

        """
        def det(u: npt.NDArray[np.float32], v: npt.NDArray[np.float32]) -> npt.NDArray[np.float32]:
            """ helper function returns determinents of two [N,2] arrays"""
            ux, uy = u[:, 0], u[:, 1]
            vx, vy = v[:, 0], v[:, 1]
            return ux*vy - uy*vx

        tv_locs: npt.NDArray[np.float32] = np.asarray([vertices[t].flatten() for t in triangles])  # triangle->vertex locations, [T x 6] array

        v0 = tv_locs[:, :2]
        v1 = np.subtract(tv_locs[:, 2:4], v0)
        v2 = np.subtract(tv_locs[:, 4: ], v0)

        b_coords: List[Tuple[Tuple[np.int32, np.float32], Tuple[np.int32, np.float32], Tuple[np.int32, np.float32]]] = []
        pin_mask: List[bool] = []

        for p_xy in points:

            p_xy = np.expand_dims(p_xy, axis=0)
            a =  (det(p_xy, v2) - det(v0, v2)) / det(v1, v2)
            b = -(det(p_xy, v1) - det(v0, v1)) / det(v1, v2)

            # find the indices of triangle containing
            in_triangle = np.bitwise_and(np.bitwise_and(a > 0, b > 0), a + b < 1)
            containing_t_idxs = np.argwhere(in_triangle)

            # if length is zero, check if on triangle(s) perimeters
            if not len(containing_t_idxs):
                on_triangle_perimeter = np.bitwise_and(np.bitwise_and(a >= 0, b >= 0), a + b <= 1)
                containing_t_idxs = np.argwhere(on_triangle_perimeter)

            # point is outside mesh. Log a warning and continue
            if not len(containing_t_idxs):
                msg = f'point {p_xy} not inside or on edge of any triangle in mesh. Skipping it'
                print(msg)
                logging.warning(msg)
                pin_mask.append(False)
                continue

            # grab the id of first triangle the point is in or on
            t_idx = int(containing_t_idxs[0])

            vertex_ids = triangles[t_idx]                               # get ids of verts in triangle
            a_xy, b_xy, c_xy = vertices[vertex_ids]                     # get xy coords of verts
            uvw = self._get_barycentric_coords(p_xy, a_xy, b_xy, c_xy)  # get barycentric coords
            b_coords.append(list(zip(vertex_ids, uvw)))                 # append to our list  # pyright: ignore[reportGeneralTypeIssues]
            pin_mask.append(True)

        return (b_coords, np.array(pin_mask, dtype=np.bool8))

    def _get_barycentric_coords(self,
                                p: npt.NDArray[np.float32],
                                a: npt.NDArray[np.float32],
                                b: npt.NDArray[np.float32],
                                c: npt.NDArray[np.float32]
                                ) -> npt.NDArray[np.float32]:
        """
        As described in Christer Ericson's Real-Time Collision Detection.
        p: the input point
        a, b, c: the vertices of the triangle

        Returns ndarray [u, v, w], the barycentric coordinates of p wrt vertices a, b, c
        """
        v0: npt.NDArray[np.float32] = np.subtract(b, a)
        v1: npt.NDArray[np.float32] = np.subtract(c, a)
        v2: npt.NDArray[np.float32] = np.subtract(p, a)
        d00: np.float32 = np.dot(v0, v0)
        d01: np.float32 = np.dot(v0, v1)
        d11: np.float32 = np.dot(v1, v1)
        d20: np.float32 = np.dot(v2, v0)
        d21: np.float32 = np.dot(v2, v1)
        denom = d00 * d11 - d01 * d01
        v: npt.NDArray[np.float32] = (d11 * d20 - d01 * d21) / denom  # pyright: ignore[reportGeneralTypeIssues]
        w: npt.NDArray[np.float32] = (d00 * d21 - d01 * d20) / denom  # pyright: ignore[reportGeneralTypeIssues]
        u: npt.NDArray[np.float32] = 1.0 - v - w

        return np.array([u, v, w]).squeeze()


def plot_mesh(vertices, triangles, pins_xy):
    """ Helper function to visualize mesh deformation outputs """
    import matplotlib.pyplot as plt

    for tri in triangles:
        x_points = []
        y_points = []
        v0, v1, v2 = tri.tolist()
        x_points.append(vertices[v0][0])
        y_points.append(vertices[v0][1])
        x_points.append(vertices[v1][0])
        y_points.append(vertices[v1][1])
        x_points.append(vertices[v2][0])
        y_points.append(vertices[v2][1])
        x_points.append(vertices[v0][0])
        y_points.append(vertices[v0][1])

        plt.plot(x_points, y_points)
    plt.ylim((-15, 15))
    plt.xlim((-15, 15))

    for pin in pins_xy:
        plt.plot(pin[0], pin[1], color='red', marker='o')

    plt.show()
