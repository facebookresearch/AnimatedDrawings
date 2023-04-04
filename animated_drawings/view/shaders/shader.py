# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import OpenGL.GL as GL
import logging


class Shader:
    """Class to create shader programs"""

    @staticmethod
    def _compile_shader(src: str, shader_type):
        with open(src, 'r') as f:
            src = f.read()
        shader = GL.glCreateShader(shader_type)

        GL.glShaderSource(shader, src)
        GL.glCompileShader(shader)

        status: bool = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
        if not status:
            log = GL.glGetShaderInfoLog(shader).decode('ascii')

            src = '\n'.join([f'{idx + 1}: {l}' for idx, l in enumerate(src.splitlines())])

            msg = f'Compile failed for {shader_type}\n{log}\n{src}'
            logging.critical(msg)
            assert False, msg

        return shader

    def __init__(self, vertex_source, fragment_source):
        """Takes paths to shader code"""
        vert = self._compile_shader(vertex_source, GL.GL_VERTEX_SHADER)
        frag = self._compile_shader(fragment_source, GL.GL_FRAGMENT_SHADER)

        if not (vert and frag):
            msg = 'Error compiling shaders'
            logging.critical(msg)
            assert False, msg

        self.glid = GL.glCreateProgram()

        GL.glAttachShader(self.glid, vert)
        GL.glAttachShader(self.glid, frag)
        GL.glLinkProgram(self.glid)
        GL.glDeleteShader(vert)
        GL.glDeleteShader(frag)

        status: bool = GL.glGetProgramiv(self.glid, GL.GL_LINK_STATUS)
        if not status:
            msg = f'Errror creating shader program: {GL.glGetProgramInfoLog(self.glid).decode("ascii")}'
            logging.critical(msg)
            assert False, msg
