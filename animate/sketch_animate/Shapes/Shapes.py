from collections import defaultdict
import itertools
import OpenGL.GL as GL
import numpy as np
import ctypes
import triangle
from sketch_animate.util import read_texture, scale


class ARAP_Rectangle:
    class ARAP_Handle:

        def __init__(self, v, v_idx):
            self.widget = Rectangle(color='blue')

            self.cx, self.cy = v[0], v[1]

            self.widget.set_position(self.cx, self.cy, 0)
            self.widget.set_uniform_scale(0.1)

            self.v_idx = v_idx

        def move_handle(self, x=None, y=None):
            if x:
                self.cx += x
            if y:
                self.cy += y
            self.widget.set_position(self.cx, self.cy, 0)

        def draw(self, **kwargs):
            self.widget.draw(**kwargs)

    def __init__(self, color='white'):
        if color == 'white':
            c = np.array([1.0, 1.0, 1.0], np.float32)
        elif color == 'black':
            c = np.array([0.00, 0.0, 0.0], np.float32)
        else:
            assert len(color) == 3
            c = np.array([*color], np.float32)

        self.points = None
        self.triangle_mesh = None
        self.generate_points()

        self.arap_handles = []
        # cvs = [25, 10, 80]
        cvs = [2, 0]
        for c in cvs:
            self.arap_handles.append(self.ARAP_Handle(self.triangle_mesh['vertices'][c], v_idx=c))

        # self.arap_handles[0].move_handle(x=2.5, y=0.5)
        # self.arap_handles[2].move_handle(x=-2.5, y=0.5)

        self.arap_solve()

        self.vao = GL.glGenVertexArrays(1)
        self.vbo = GL.glGenBuffers(1)
        # self.ebo = GL.glGenBuffers(1)

        self.model = np.identity(4, np.float32)

        GL.glBindVertexArray(self.vao)

        # buffer vertex data
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.points, GL.GL_STATIC_DRAW)

        # buffer element index data
        # GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        # GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.indices, GL.GL_STATIC_DRAW)

        # position attributes
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 4 * self.points.shape[1], None)
        GL.glEnableVertexAttribArray(0)

        # color attributes
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, False, 4 * self.points.shape[1], ctypes.c_void_p(4 * 3))
        GL.glEnableVertexAttribArray(1)

        # texture attributes
        GL.glVertexAttribPointer(2, 2, GL.GL_FLOAT, False, 4 * self.points.shape[1], ctypes.c_void_p(4 * 6))
        GL.glEnableVertexAttribArray(2)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def arap_solve(self):
        w = 1000
        edge_indices = []

        for triangle in self.triangle_mesh['triangles']:
            e1 = sorted([triangle[0], triangle[1]])
            e2 = sorted([triangle[1], triangle[2]])
            e3 = sorted([triangle[2], triangle[0]])
            edge_indices.append(tuple(e1))
            edge_indices.append(tuple(e2))
            edge_indices.append(tuple(e3))

        edge_indices = list(set(edge_indices))

        ###############################
        # Begin 4.1, Baseline algorithm
        ###############################
        A = np.zeros((len(edge_indices) + len(self.arap_handles), len(self.triangle_mesh['vertices'])))
        for idx, e in enumerate(edge_indices):
            A[idx, e[1]] = 1
            A[idx, e[0]] = -1

        for idx, c in enumerate(self.arap_handles):
            A[len(edge_indices) + idx, c.v_idx] = w

        B = np.zeros((A.shape[0], 2))
        for idx, e in enumerate(edge_indices):
            v0 = self.triangle_mesh['vertices'][e[0]]
            v1 = self.triangle_mesh['vertices'][e[1]]
            B[idx, 0] = v1[0] - v0[0]
            B[idx, 1] = v1[1] - v0[1]
        for idx, c in enumerate(self.arap_handles):
            B[len(edge_indices) + idx, 0] = w * c.cx
            B[len(edge_indices) + idx, 1] = w * c.cy

        a = np.matmul(A.T, A)
        bx = np.matmul(A.T, B[:, 0])
        by = np.matmul(A.T, B[:, 1])

        vx = np.linalg.solve(a, bx)
        vy = np.linalg.solve(a, by)

        for idx, tri in enumerate(self.triangle_mesh['triangles']):
            for jdx, vert_idx in enumerate(tri):  # reversed so it faces camera
                vert = self.triangle_mesh['vertices'][vert_idx]
                self.points[3 * idx + jdx, 0] = vx[vert_idx]
                self.points[3 * idx + jdx, 1] = vy[vert_idx]
        # return
        ###############################
        # End 4.1, Baseline algorithm
        ###############################

        ###############################
        # Start 4.2, First Step: Similarity Transformation
        ###############################

        edge_neighbors = defaultdict(list)
        for triangle in self.triangle_mesh['triangles']:

            for i, j in list(itertools.product(triangle, triangle)):
                if i == j:
                    continue
                edge = tuple(sorted([i, j]))
                edge_neighbors[edge] += list(triangle)

        for key, val in edge_neighbors.items():
            edge_neighbors[key] = list(set(val))
            edge_neighbors[key].remove(key[0])
            edge_neighbors[key].remove(key[1])
            edge_neighbors[key].insert(0, key[0])
            edge_neighbors[key].insert(1, key[1])

        def orientation(p1, p2, p3):

            # to find the orientation of
            # an ordered triplet (p1,p2,p3)
            # function returns the following values:
            # 0 : Colinear points
            # 1 : Clockwise points
            # 2 : Counterclockwise
            val = (float(p2[1] - p1[1]) * (p3[0] - p2[0])) - \
                  (float(p2[0] - p1[0]) * (p3[1] - p2[1]))
            if val > 0:
                # Clockwise orientation
                return 1
            elif val < 0:
                # Counterclockwise orientation
                return 2
            else:
                # Colinear orientation
                return 0

        """
        for key, val in edge_neighbors.items():
            #based on direction of edge, set vl and vr up.
            # vl goes at index [2] vr goes at index [3]
            p1_idx = edge_neighbors[key][1]
            p2_idx = edge_neighbors[key][2]
            p3_idx = edge_neighbors[key][3]

            p1 = self.triangle_mesh['vertices'][p1_idx]
            p2 = self.triangle_mesh['vertices'][p2_idx]
            p3 = self.triangle_mesh['vertices'][p3_idx]
            orient = orientation(p1, p2, p3)
            if orient == 1:
                edge_neighbors[key][2] = p2_idx
                edge_neighbors[key][3] = p3_idx
            elif orient == 2:
                edge_neighbors[key][2] = p3_idx
                edge_neighbors[key][3] = p2_idx
            else:
                p0_idx = edge_neighbors[key][0]
                p2_idx = edge_neighbors[key][2]
                p3_idx = edge_neighbors[key][3]

                p0 = self.triangle_mesh['vertices'][p0_idx]
                p2 = self.triangle_mesh['vertices'][p2_idx]
                p3 = self.triangle_mesh['vertices'][p3_idx]
                orient = orientation(p0, p2, p3)
                if orient == 1:
                    edge_neighbors[key][2] = p3_idx
                    edge_neighbors[key][3] = p2_idx
                elif orient == 2:
                    edge_neighbors[key][2] = p2_idx
                    edge_neighbors[key][3] = p3_idx
                else:
                    assert False, 'colinear points'

            """

        A = np.zeros((
            2 * len(edge_neighbors.items()) + 2 * len(self.arap_handles),
            2 * (len(self.triangle_mesh['vertices']))
        ))
        for edx, e in enumerate(edge_neighbors.keys()):

            G = np.empty([2 * len(edge_neighbors[e]), 2])
            for idx, v_idx in enumerate(edge_neighbors[e]):
                v = self.triangle_mesh['vertices'][v_idx]
                G[2 * idx] = v[0], v[1]
                G[2 * idx + 1] = v[1], -v[0]

            e_x, e_y = self.triangle_mesh['vertices'][e[1]] - self.triangle_mesh['vertices'][e[0]]

            E = np.array([
                [e_x, e_y],
                [e_y, -e_x]
            ])

            Q = np.zeros((2, 2 * len(edge_neighbors[e])))
            Q[0, 0] = -1
            Q[1, 1] = -1
            Q[0, 2] = 1
            Q[1, 3] = 1

            H = Q - np.matmul(E, np.matmul(np.linalg.inv(np.matmul(G.T, G)), G.T))
            for idx, vdx in enumerate(edge_neighbors[e]):
                block = H[:, 2 * idx:2 * (idx + 1)]
                A[2 * edx:2 * (edx + 1), 2 * vdx:2 * (vdx + 1)] = block

        B = np.zeros((2 * len(edge_neighbors.items()) + 2 * len(self.arap_handles), 1))

        for cdx, c in enumerate(self.arap_handles):
            A[2 * len(edge_neighbors.items()) + 2 * cdx, 2 * c.v_idx] = w
            A[2 * len(edge_neighbors.items()) + 2 * cdx + 1, 2 * c.v_idx + 1] = w

            B[2 * len(edge_neighbors.items()) + 2 * cdx] = w * c.cx
            B[2 * len(edge_neighbors.items()) + 2 * cdx + 1] = w * c.cy

        V = np.linalg.solve(np.matmul(A.T, A), np.matmul(A.T, B))

        for idx, tri in enumerate(self.triangle_mesh['triangles']):
            for jdx, vert_idx in enumerate(tri):  # reversed so it faces camera
                points_idx = 3 * idx + jdx
                self.points[3 * idx + jdx, 0] = V[2 * vert_idx]
                self.points[3 * idx + jdx, 1] = V[2 * vert_idx + 1]

        ###############################
        # End 4.2, First Step: Similarity Transformation
        ###############################

        ###############################
        # Start 4.3, Second Step: Scale Adjustment
        ###############################

        edge_neighbors = defaultdict(list)
        for triangle in self.triangle_mesh['triangles']:

            for i, j in list(itertools.product(triangle, triangle)):
                if i == j:
                    continue
                edge = tuple(sorted([i, j]))
                edge_neighbors[edge] += list(triangle)

        for key, val in edge_neighbors.items():
            edge_neighbors[key] = list(set(val))
            edge_neighbors[key].remove(key[0])
            edge_neighbors[key].remove(key[1])
            edge_neighbors[key].insert(0, key[0])
            edge_neighbors[key].insert(1, key[1])

        A = np.zeros((
            2 * len(edge_neighbors.items()) + 2 * len(self.arap_handles),
            2 * (len(self.triangle_mesh['vertices']))
        ))
        for edx, e in enumerate(edge_neighbors.keys()):

            G = np.empty([2 * len(edge_neighbors[e]), 2])
            for idx, v_idx in enumerate(edge_neighbors[e]):
                v = self.triangle_mesh['vertices'][v_idx]
                G[2 * idx] = v[0], v[1]
                G[2 * idx + 1] = v[1], -v[0]

            e_x, e_y = self.triangle_mesh['vertices'][e[1]] - self.triangle_mesh['vertices'][e[0]]

            E = np.array([
                [e_x, e_y],
                [e_y, -e_x]
            ])

            Q = np.zeros((2, 2 * len(edge_neighbors[e])))
            Q[0, 0] = -1
            Q[1, 1] = -1
            Q[0, 2] = 1
            Q[1, 3] = 1

            H = Q - np.matmul(E, np.matmul(np.linalg.inv(np.matmul(G.T, G)), G.T))
            for idx, vdx in enumerate(edge_neighbors[e]):
                block = H[:, 2 * idx:2 * (idx + 1)]
                A[2 * edx:2 * (edx + 1), 2 * vdx:2 * (vdx + 1)] = block

        B = np.zeros((2 * len(edge_neighbors.items()) + 2 * len(self.arap_handles), 1))

        for cdx, c in enumerate(self.arap_handles):
            A[2 * len(edge_neighbors.items()) + 2 * cdx, 2 * c.v_idx] = w
            A[2 * len(edge_neighbors.items()) + 2 * cdx + 1, 2 * c.v_idx + 1] = w

            B[2 * len(edge_neighbors.items()) + 2 * cdx] = w * c.cx
            B[2 * len(edge_neighbors.items()) + 2 * cdx + 1] = w * c.cy

        V = np.linalg.solve(np.matmul(A.T, A), np.matmul(A.T, B))

        A2 = np.zeros((len(edge_neighbors.keys()) + len(self.arap_handles), self.triangle_mesh['vertices'].shape[0]))

        E2x = np.zeros((len(edge_neighbors.keys()) + len(self.arap_handles)))
        E2y = np.zeros((len(edge_neighbors.keys()) + len(self.arap_handles)))

        for edx, e in enumerate(edge_neighbors.keys()):

            G = np.empty([2 * len(edge_neighbors[e]), 2])
            N = np.empty([2 * len(edge_neighbors[e])])
            for idx, v_idx in enumerate(edge_neighbors[e]):
                v = self.triangle_mesh['vertices'][v_idx]
                G[2 * idx] = v[0], v[1]
                G[2 * idx + 1] = v[1], -v[0]
                N[2 * idx] = V[2 * v_idx]
                N[2 * idx + 1] = V[2 * v_idx + 1]
                # N[2*idx] = v[0]
                # N[2*idx+1] = v[1]

            ck, sk = np.matmul(np.matmul(np.linalg.inv(np.matmul(G.T, G)), G.T), N)
            Tk = (1 / (ck ** 2 + sk ** 2)) * np.array([[ck, sk], [-sk, ck]])

            A2[edx, e[0]] = -1
            A2[edx, e[1]] = 1

            E2x[edx] = np.matmul(Tk, self.triangle_mesh['vertices'][e[1]] - self.triangle_mesh['vertices'][e[0]])[0]
            E2y[edx] = np.matmul(Tk, self.triangle_mesh['vertices'][e[1]] - self.triangle_mesh['vertices'][e[0]])[1]

        for cdx, c in enumerate(self.arap_handles):
            A2[len(edge_neighbors.keys()) + cdx, c.v_idx] = w
            E2x[len(edge_neighbors.keys()) + cdx] = w * c.cx
            E2y[len(edge_neighbors.keys()) + cdx] = w * c.cy

        Vx = np.linalg.solve(np.matmul(A2.T, A2), np.matmul(A2.T, E2x))
        Vy = np.linalg.solve(np.matmul(A2.T, A2), np.matmul(A2.T, E2y))
        x = 2
        for idx, tri in enumerate(self.triangle_mesh['triangles']):
            for jdx, vert_idx in enumerate(tri):  # reversed so it faces camera
                points_idx = 3 * idx + jdx
                self.points[3 * idx + jdx, 0] = Vx[vert_idx]
                self.points[3 * idx + jdx, 1] = Vy[vert_idx]

        ###############################
        # End 4.3, Second Step: Scale Adjustment
        ###############################

        # GL.glBindVertexArray(self.vao)

        # # buffer vertex data
        # GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        # GL.glBufferData(GL.GL_ARRAY_BUFFER, self.points, GL.GL_STATIC_DRAW)

        # # buffer element index data
        # #GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        # #GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.indices, GL.GL_STATIC_DRAW)

        # # position attributes
        # GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 4*self.points.shape[1], None)
        # GL.glEnableVertexAttribArray(0)

        # GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        # GL.glBindVertexArray(0)

    def generate_points(self):
        verts = [
            [0.5, 0.5],
            [-0.5, 0.5],
            [-0.5, -0.5],
            [0.5, -0.5]
        ]

        segs = [
            [0, 1],
            [1, 2],
            [2, 3],
            [3, 0],
        ]

        a = dict(vertices=verts, segments=segs, holes=[[-1, -1]])
        self.triangle_mesh = triangle.triangulate(a, 'qa.5')  # 'qa0.1') #'gp10'

        self.points = np.empty([3 * len(self.triangle_mesh['triangles']), 6], np.float32)
        for idx, tri in enumerate(self.triangle_mesh['triangles']):
            for jdx, vert_idx in enumerate(tri):  # reversed so it faces camera
                vert = self.triangle_mesh['vertices'][vert_idx]
                x = vert[0]
                y = vert[1]
                self.points[3 * idx + jdx] = x, y, 0, 0, 0, 0  # pos x3, color x3, texture x2

    def draw(self, **kwargs):

        # self.arap_handles[2].move_handle(x=0.005)
        # self.arap_handles[0].move_handle(y=0.005)
        self.arap_handles[0].move_handle(x=-0.005, y=0.005)
        # self.arap_handles[1].move_handle(y=-0.005)
        self.arap_solve()

        GL.glDisable(GL.GL_CULL_FACE)

        GL.glBindVertexArray(self.vao)

        # buffer vertex data
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.points, GL.GL_STATIC_DRAW)

        # position attributes
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 4 * self.points.shape[1], None)
        GL.glEnableVertexAttribArray(0)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
        GL.glUseProgram(kwargs['shader_ids']['color_shader'])

        model_loc = GL.glGetUniformLocation(kwargs['shader_ids']['color_shader'], "model")
        GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE, self.model.T)

        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.points.shape[0])

        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)

        for handle in self.arap_handles:
            handle.draw(**kwargs)


class Rectangle:

    def __init__(self, color='white'):
        if color == 'white':
            c = np.array([1.0, 1.0, 1.0], np.float32)
        elif color == 'black':
            c = np.array([0.00, 0.0, 0.0], np.float32)
        elif color == 'blue':
            c = np.array([0.00, 0.0, 1.0], np.float32)
        else:
            assert len(color) == 3
            c = np.array([*color], np.float32)

        #                         ---position---  color

        self.points = np.array([
            [0.5, 0.5, 0.0, *c],  # top right
            [-0.5, 0.5, 0.0, *c],  # top left
            [-0.5, -0.5, 0.0, *c],  # bottom left
            [0.5, -0.5, 0.0, *c],  # bottom right
            [0.5, 0.5, 0.0, *c],  # top right
            [-0.5, -0.5, 0.0, *c],  # bottom left
        ], np.float32)

        # self.indices = np.array([3, 1, 0,  # first triangle
        #                         3, 2, 1   # second triangle
        #                         ], np.uint)

        self.vao = GL.glGenVertexArrays(1)
        self.vbo = GL.glGenBuffers(1)
        # self.ebo = GL.glGenBuffers(1)

        self.model = np.identity(4, np.float32)
        self.scale = np.identity(4, np.float32)

        def set_position(self, x, y, z):
            self.model[0, -1] = x
            self.model[1, -1] = y
            self.model[2, -1] = z

        GL.glBindVertexArray(self.vao)

        # buffer vertex data
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.points, GL.GL_STATIC_DRAW)

        # buffer element index data
        # GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        # GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.indices, GL.GL_STATIC_DRAW)

        # position attributes
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 4 * self.points.shape[1], None)
        GL.glEnableVertexAttribArray(0)

        # color attributes
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, False, 4 * self.points.shape[1], ctypes.c_void_p(4 * 3))
        GL.glEnableVertexAttribArray(1)

        # texture attributes
        GL.glVertexAttribPointer(2, 2, GL.GL_FLOAT, False, 4 * self.points.shape[1], ctypes.c_void_p(4 * 6))
        GL.glEnableVertexAttribArray(2)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def set_position(self, x, y, z):
        self.model[0, -1] = x
        self.model[1, -1] = y
        self.model[2, -1] = z

    def set_uniform_scale(self, s):
        self.scale = scale(s, s, s)

    def draw(self, **kwargs):

        GL.glUseProgram(kwargs['shader_ids']['color_shader'])
        model_loc = GL.glGetUniformLocation(kwargs['shader_ids']['color_shader'], "model")
        GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE, self.scale.T @ self.model.T)

        GL.glBindVertexArray(self.vao)
        # GL.glDrawElements(GL.GL_TRIANGLES, 6, GL.GL_UNSIGNED_INT, None)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)


class ScreenSpaceSquare:
    def __init__(self, x, y, color=None):
        if color is None:
            c = np.array([0.00, 0.0, 0.0], np.float32)
        else:
            assert len(color) == 3
            c = np.array([*color], np.float32)

        width = 0.01
        x = (x - width, x + width)
        y = (y - width, y + width)

        self.points = np.array([
            [x[1], y[1], 0.0, *c],  # top right
            [x[0], y[1], 0.0, *c],  # top left
            [x[0], y[0], 0.0, *c],  # bottom left
            [x[1], y[0], 0.0, *c],  # bottom right
            [x[1], y[1], 0.0, *c],  # top right
            [x[0], y[0], 0.0, *c],  # bottom left
        ], np.float32)

        self.vao = GL.glGenVertexArrays(1)
        self.vbo = GL.glGenBuffers(1)

        GL.glBindVertexArray(self.vao)

        # buffer vertex data
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.points, GL.GL_STATIC_DRAW)

        # position attributes
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 4 * self.points.shape[1], None)
        GL.glEnableVertexAttribArray(0)

        # color attributes
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, False, 4 * self.points.shape[1], ctypes.c_void_p(4 * 3))
        GL.glEnableVertexAttribArray(1)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def update_position(self, x, y):
        width = 0.01
        x = (x - width, x + width)
        y = (y - width, y + width)

        self.points[:, 0:2] = np.array([
            [x[1], y[1]],  # top right
            [x[0], y[1]],  # top left
            [x[0], y[0]],  # bottom left
            [x[1], y[0]],  # bottom right
            [x[1], y[1]],  # top right
            [x[0], y[0]],  # bottom left
        ], np.float32)

        GL.glBindVertexArray(self.vao)

        # buffer vertex data
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.points, GL.GL_STATIC_DRAW)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def draw(self, **kwargs):
        GL.glUseProgram(kwargs['shader_ids']['border_shader'])

        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.points.shape[0])
        GL.glBindVertexArray(0)


class Border:

    def __init__(self, color=None):
        if color is None:
            c = np.array([0.00, 0.0, 0.0], np.float32)
        else:
            assert len(color) == 3
            c = np.array([*color], np.float32)

        #                         ---position---  color

        self.points = np.empty([24, 6], np.float32)

        border_width = 0.01
        # border top
        x = (-1, 1)
        y = (1 - border_width, 1)
        top = (x, y)
        # border bottom
        x = (-1, 1)
        y = (-1, -1 + border_width)
        bottom = (x, y)
        # border left
        x = (-1, -1 + border_width / 2)
        y = (-1, 1)
        left = (x, y)
        # border right
        x = (1 - border_width / 2, 1)
        y = (-1, 1)
        right = (x, y)

        for idx, (x, y) in enumerate([top, bottom, right, left]):
            self.points[idx * 6:idx * 6 + 6, :] = [
                [x[1], y[1], 0.0, *c],  # top right
                [x[0], y[1], 0.0, *c],  # top left
                [x[0], y[0], 0.0, *c],  # bottom left
                [x[1], y[0], 0.0, *c],  # bottom right
                [x[1], y[1], 0.0, *c],  # top right
                [x[0], y[0], 0.0, *c],  # bottom left
            ]

        self.vao = GL.glGenVertexArrays(1)
        self.vbo = GL.glGenBuffers(1)
        # self.ebo = GL.glGenBuffers(1)

        self.model = np.identity(4, np.float32)

        GL.glBindVertexArray(self.vao)

        # buffer vertex data
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.points, GL.GL_STATIC_DRAW)

        # buffer element index data
        # GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        # GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.indices, GL.GL_STATIC_DRAW)

        # position attributes
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 4 * self.points.shape[1], None)
        GL.glEnableVertexAttribArray(0)

        # color attributes
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, False, 4 * self.points.shape[1], ctypes.c_void_p(4 * 3))
        GL.glEnableVertexAttribArray(1)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def draw(self, **kwargs):

        GL.glUseProgram(kwargs['shader_ids']['border_shader'])

        GL.glBindVertexArray(self.vao)
        # GL.glDrawElements(GL.GL_TRIANGLES, 6, GL.GL_UNSIGNED_INT, None)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.points.shape[0])


class Triangle:

    def __init__(self):
        #                         positions       colors
        self.points = np.array([
            [0.0, 0.5, 0.0, 0.0, 1.0, 0.0],  # top middle
            [-0.5, -0.5, 0.0, 0.0, 0.0, 1.0],  # bottom left
            [0.5, -0.5, 0.0, 1.0, 0.0, 0.0],  # bottom right
        ], np.float32)
        self.model = np.identity(4, np.float32)

        self.texCoords = np.array([
            1.0, 0.0,  # bottom right
            0.5, 1.0,  # top middle
            0.0, 0.0  # bottom left
        ])

        self.vbo = GL.glGenBuffers(1)  # vertex buffer id
        self.vao = GL.glGenVertexArrays(1)

        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.points, GL.GL_STATIC_DRAW)

        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 6 * 4, None)
        GL.glEnableVertexAttribArray(0)

        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, False, 6 * 4, ctypes.c_void_p(4 * 3))
        GL.glEnableVertexAttribArray(1)

    def draw(self, **kwargs):
        GL.glUseProgram(kwargs['shader_ids']['color_shader'])
        model_loc = GL.glGetUniformLocation(kwargs['shader_ids']['color_shader'], "model")
        GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE, self.model)

        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)


class Drawing:

    def __init__(self, color='white', drawing_fn=None):
        if color == 'white':
            c = np.array([1.0, 1.0, 1.0], np.float32)
        elif color == 'black':
            c = np.array([0.00, 0.0, 0.0], np.float32)
        elif color == 'blue':
            c = np.array([0.00, 0.0, 1.0], np.float32)
        else:
            assert len(color) == 3
            c = np.array([*color], np.float32)

        self.tid0 = read_texture(drawing_fn, GL.GL_RGBA)
        #                         ---position---  color

        self.points = np.array([
            [0.5, 0.5, 0.0, *c, 1.0, 1.0],  # top right
            [-0.5, 0.5, 0.0, *c, 0.0, 1.0],  # top left
            [-0.5, -0.5, 0.0, *c, 0.0, 0.0],  # bottom left
            [0.5, -0.5, 0.0, *c, 1.0, 0.0],  # bottom right
            [0.5, 0.5, 0.0, *c, 1.0, 1.0],  # top right
            [-0.5, -0.5, 0.0, *c, 0.0, 0.0],  # bottom left
        ], np.float32)

        # self.indices = np.array([3, 1, 0,  # first triangle
        #                         3, 2, 1   # second triangle
        #                         ], np.uint)

        self.vao = GL.glGenVertexArrays(1)
        self.vbo = GL.glGenBuffers(1)
        # self.ebo = GL.glGenBuffers(1)

        self.model = np.identity(4, np.float32)
        self.scale = np.identity(4, np.float32)

        def set_position(self, x, y, z):
            self.model[0, -1] = x
            self.model[1, -1] = y
            self.model[2, -1] = z

        GL.glBindVertexArray(self.vao)

        # buffer vertex data
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.points, GL.GL_STATIC_DRAW)

        # buffer element index data
        # GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        # GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.indices, GL.GL_STATIC_DRAW)

        # position attributes
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 4 * self.points.shape[1], None)
        GL.glEnableVertexAttribArray(0)

        # color attributes
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, False, 4 * self.points.shape[1], ctypes.c_void_p(4 * 3))
        GL.glEnableVertexAttribArray(1)

        # texture attributes
        GL.glVertexAttribPointer(2, 2, GL.GL_FLOAT, False, 4 * self.points.shape[1], ctypes.c_void_p(4 * 6))
        GL.glEnableVertexAttribArray(2)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def set_position(self, x, y, z):
        self.model[0, -1] = x
        self.model[1, -1] = y
        self.model[2, -1] = z

    def set_uniform_scale(self, s):
        self.scale = scale(s, s, s)

    def draw(self, **kwargs):

        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.tid0)

        GL.glUseProgram(kwargs['shader_ids']['texture_shader'])
        model_loc = GL.glGetUniformLocation(kwargs['shader_ids']['texture_shader'], "model")
        # GL.glUseProgram(kwargs['shader_ids']['color_shader'])
        # model_loc = GL.glGetUniformLocation(kwargs['shader_ids']['color_shader'], "model")
        GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE, self.scale.T @ self.model.T)

        GL.glBindVertexArray(self.vao)
        # GL.glDrawElements(GL.GL_TRIANGLES, 6, GL.GL_UNSIGNED_INT, None)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)
