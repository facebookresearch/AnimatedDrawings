import numpy as np
import OpenGL.GL as GL
import ctypes

class Box:

    def __init__(self, shader_name='color_shader'):
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

        self.indices = np.array([ 2,  1,  0,
                                  5,  4,  3,
                                  6,  7,  8,
                                  9, 10, 11,
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


        self.shader_name = shader_name
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

        # position attributes
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 4*self.points.shape[1], None)  # 4 is byte size of np.float32
        GL.glEnableVertexAttribArray(0)

        # color attributes
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, False, 4*self.points.shape[1], ctypes.c_void_p(4*3))  # 4 is byte size of np.float32
        GL.glEnableVertexAttribArray(1)

        # normals attributes
        GL.glVertexAttribPointer(2, 3, GL.GL_FLOAT, False, 4*self.points.shape[1], ctypes.c_void_p(4*6))  # 4 is byte size of np.float32
        GL.glEnableVertexAttribArray(2)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        self.model = np.identity(4, np.float32)

    def rebuffer_vertex_data(self):
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.points, GL.GL_STATIC_DRAW)

    def draw(self, **kwargs):

        GL.glUseProgram(kwargs['shader_ids'][self.shader_name])
        model_loc = GL.glGetUniformLocation(kwargs['shader_ids'][self.shader_name], "model")
        GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE, self.model.T)

        if self.shader_name == 'lighting_shader':
            m_ambient_loc = GL.glGetUniformLocation(kwargs['shader_ids'][self.shader_name], "material.ambient")
            GL.glUniform3fv(m_ambient_loc, 1, self.material['ambient'])
            m_diffuse_loc = GL.glGetUniformLocation(kwargs['shader_ids'][self.shader_name], "material.diffuse")
            GL.glUniform3fv(m_diffuse_loc, 1, self.material['diffuse'])
            m_specular_loc = GL.glGetUniformLocation(kwargs['shader_ids'][self.shader_name], "material.specular")
            GL.glUniform3fv(m_specular_loc, 1, self.material['specular'])
            m_shininess_loc = GL.glGetUniformLocation(kwargs['shader_ids'][self.shader_name], "material.shininess")
            GL.glUniform1f(m_shininess_loc, self.material['shininess'])

        GL.glBindVertexArray(self.vao)
        #GL.glDrawElements(GL.GL_TRIANGLES, 3, GL.GL_UNSIGNED_INT, ctypes.c_void_p(3 * 4))
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 36)
