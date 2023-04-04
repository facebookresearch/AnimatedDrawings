# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import numpy as np
import OpenGL.GL as GL
import ctypes
from animated_drawings.model.transform import Transform


class Box(Transform):

    def __init__(self, shader_name: str = 'color_shader') -> None:
        super().__init__()

        self.points = np.array([
            [ 0.5,  0.5, -0.5,  0.0, 0.0, 0.0, 0.0,  0.0, -1.0],
            [ 0.5, -0.5, -0.5,  0.0, 0.0, 0.0, 0.0,  0.0, -1.0],
            [-0.5, -0.5, -0.5,  0.0, 0.0, 0.0, 0.0,  0.0, -1.0],
            [-0.5, -0.5, -0.5,  0.0, 0.0, 0.0, 0.0,  0.0, -1.0],
            [-0.5,  0.5, -0.5,  0.0, 0.0, 0.0, 0.0,  0.0, -1.0],
            [ 0.5,  0.5, -0.5,  0.0, 0.0, 0.0, 0.0,  0.0, -1.0],

            [-0.5, -0.5,  0.5,  0.0, 0.0, 0.0, 0.0,  0.0,  1.0],
            [ 0.5, -0.5,  0.5,  0.0, 0.0, 0.0, 0.0,  0.0,  1.0],
            [ 0.5,  0.5,  0.5,  0.0, 0.0, 0.0, 0.0,  0.0,  1.0],
            [ 0.5,  0.5,  0.5,  0.0, 0.0, 0.0, 0.0,  0.0,  1.0],
            [-0.5,  0.5,  0.5,  0.0, 0.0, 0.0, 0.0,  0.0,  1.0],
            [-0.5, -0.5,  0.5,  0.0, 0.0, 0.0, 0.0,  0.0,  1.0],

            [ 0.5, -0.5, -0.5,  0.0, 0.0, 0.0, 1.0,  0.0,  0.0],
            [ 0.5,  0.5, -0.5,  0.0, 0.0, 0.0, 1.0,  0.0,  0.0],
            [ 0.5,  0.5,  0.5,  0.0, 0.0, 0.0, 1.0,  0.0,  0.0],
            [ 0.5,  0.5,  0.5,  0.0, 0.0, 0.0, 1.0,  0.0,  0.0],
            [ 0.5, -0.5,  0.5,  0.0, 0.0, 0.0, 1.0,  0.0,  0.0],
            [ 0.5, -0.5, -0.5,  0.0, 0.0, 0.0, 1.0,  0.0,  0.0],

            [-0.5,  0.5,  0.5, 0.0, 0.0, 0.0, -1.0,  0.0,  0.0],
            [-0.5,  0.5, -0.5, 0.0, 0.0, 0.0, -1.0,  0.0,  0.0],
            [-0.5, -0.5, -0.5, 0.0, 0.0, 0.0, -1.0,  0.0,  0.0],
            [-0.5, -0.5, -0.5, 0.0, 0.0, 0.0, -1.0,  0.0,  0.0],
            [-0.5, -0.5,  0.5, 0.0, 0.0, 0.0, -1.0,  0.0,  0.0],
            [-0.5,  0.5,  0.5, 0.0, 0.0, 0.0, -1.0,  0.0,  0.0],

            [-0.5, -0.5, -0.5,  0.0, 0.0, 0.0, 0.0, -1.0,  0.0],
            [ 0.5, -0.5, -0.5,  0.0, 0.0, 0.0, 0.0, -1.0,  0.0],
            [ 0.5, -0.5,  0.5,  0.0, 0.0, 0.0, 0.0, -1.0,  0.0],
            [ 0.5, -0.5,  0.5,  0.0, 0.0, 0.0, 0.0, -1.0,  0.0],
            [-0.5, -0.5,  0.5,  0.0, 0.0, 0.0, 0.0, -1.0,  0.0],
            [-0.5, -0.5, -0.5,  0.0, 0.0, 0.0, 0.0, -1.0,  0.0],

            [ 0.5,  0.5,  0.5,  0.0, 0.0, 0.0, 0.0,  1.0,  0.0],
            [ 0.5,  0.5, -0.5,  0.0, 0.0, 0.0, 0.0,  1.0,  0.0],
            [-0.5,  0.5, -0.5,  0.0, 0.0, 0.0, 0.0,  1.0,  0.0],
            [-0.5,  0.5, -0.5,  0.0, 0.0, 0.0, 0.0,  1.0,  0.0],
            [-0.5,  0.5,  0.5,  0.0, 0.0, 0.0, 0.0,  1.0,  0.0],
            [ 0.5,  0.5,  0.5,  0.0, 0.0, 0.0, 0.0,  1.0,  0.0],

        ], np.float32)

        self.indices = np.array([2,   1,  0,
                                 5,   4,  3,
                                 6,   7,  8,
                                 9,  10, 11,
                                 14, 13, 12,
                                 17, 16, 15,
                                 18, 19, 20,
                                 21, 22, 23,
                                 24, 25, 26,
                                 27, 28, 29,
                                 32, 31, 30,
                                 35, 34, 33
                                 ], np.uint32)

        self.material = {
            'ambient': np.array([0.4, 0.4, 0.4], np.float32),
            'diffuse': np.array([0.4, 0.4, 0.4], np.float32),
            'specular': np.array([0.3, 0.0, 0.0], np.float32),
            'shininess': 32
        }

        self.shader_name: str = shader_name

        self._is_opengl_initialized: bool = False  # keep track of whether self._initialize_opengl_resources was called.

    def _initialize_opengl_resources(self) -> None:
        """ Method to initialize the OpenGL arrays and buffers necessary to draw the object.
        It's better to not initialize these things unless we're definitely going to be drawing the object,
        as calling GL functions without calling glfw.init() first can cause a mysterious segfault.
        This way, unit tests and other non-rendering operations can proceed without requiring a Controller.
        """
        self.vao = GL.glGenVertexArrays(1)
        self.vbo = GL.glGenBuffers(1)
        self.ebo = GL.glGenBuffers(1)

        GL.glBindVertexArray(self.vao)

        # buffer vertex data
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.points, GL.GL_STATIC_DRAW)

        # buffer element index data
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.indices, GL.GL_STATIC_DRAW)

        vert_bytes     = 4 * self.points.shape[1]  # 4 is byte size of np.float32
        pos_offset     = 4 * 0
        color_offset   = 4 * 3
        normals_offset = 4 * 6

        # position attributes
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, vert_bytes, ctypes.c_void_p(pos_offset))
        GL.glEnableVertexAttribArray(0)

        # color attributes
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, False, vert_bytes, ctypes.c_void_p(color_offset))
        GL.glEnableVertexAttribArray(1)

        # normals attributes
        GL.glVertexAttribPointer(2, 3, GL.GL_FLOAT, False, vert_bytes, ctypes.c_void_p(normals_offset))
        GL.glEnableVertexAttribArray(2)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        self._is_opengl_initialized = True

    def rebuffer_vertex_data(self) -> None:
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.points, GL.GL_STATIC_DRAW)

    def _draw(self, **kwargs) -> None:

        if not self._is_opengl_initialized:
            self._initialize_opengl_resources()

        GL.glUseProgram(kwargs['shader_ids'][self.shader_name])
        model_loc = GL.glGetUniformLocation(kwargs['shader_ids'][self.shader_name], "model")
        GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE, self._world_transform.T)

        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 36)
