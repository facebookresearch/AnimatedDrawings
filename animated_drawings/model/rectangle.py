# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import numpy as np
import OpenGL.GL as GL
from animated_drawings.model.transform import Transform
import ctypes


class Rectangle(Transform):

    def __init__(self, color: str = 'white') -> None:

        super().__init__()

        if color == 'white':
            c = np.array([1.0, 1.0, 1.0], np.float32)
        elif color == 'black':
            c = np.array([0.3, 0.3, 0.3], np.float32)
        elif color == 'blue':
            c = np.array([0.00, 0.0, 1.0], np.float32)
        else:
            assert len(color) == 3
            c = np.array([*color], np.float32)

        self.points = np.array([
            [0.5, 0.0,  0.5, *c],  # top right
            [-0.5, 0.0, -0.5, *c],  # bottom left
            [-0.5, 0.0,  0.5, *c],  # top left
            [0.5, 0.0, -0.5, *c],  # bottom right
            [-0.5, 0.0, -0.5, *c],  # bottom left
            [0.5, 0.0,  0.5, *c],  # top right
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

        # texture attributes
        GL.glVertexAttribPointer(2, 2, GL.GL_FLOAT, False, 4 * self.points.shape[1], ctypes.c_void_p(4 * 6))
        GL.glEnableVertexAttribArray(2)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def _draw(self, **kwargs) -> None:

        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        GL.glUseProgram(kwargs['shader_ids']['color_shader'])
        model_loc = GL.glGetUniformLocation(kwargs['shader_ids']['color_shader'], "model")
        GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE, self._world_transform.T)

        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)
