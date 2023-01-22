# Copyright (c) Meta Platforms, Inc. and affiliates.

from model.animated_drawing import AnimatedDrawing

def test_init():
    import OpenGL.GL as GL
    import glfw;
    glfw.init()
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    win = glfw.create_window(100, 100, 'Viewer', None, None)
    glfw.make_context_current(win)

    cfg_fn = 'animate/animator/tests/test_character/nick_cat.yaml'
    AnimatedDrawing(cfg_fn)
    assert True

    # TODO: Add more specifics to test
