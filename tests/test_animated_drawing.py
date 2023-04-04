# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from animated_drawings.model.animated_drawing import AnimatedDrawing
from animated_drawings.config import Config
from pkg_resources import resource_filename


def test_init():
    import OpenGL.GL as GL
    import glfw
    glfw.init()
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    win = glfw.create_window(100, 100, 'Viewer', None, None)
    glfw.make_context_current(win)

    mvc_cfg_fn = resource_filename(__name__, 'test_animated_drawing_files/test_mvc.yaml')
    mvc_config = Config(mvc_cfg_fn)
    char_cfg, retarget_cfg, motion_cfg = mvc_config.scene.animated_characters[0]

    AnimatedDrawing(char_cfg, retarget_cfg, motion_cfg)

    assert True
