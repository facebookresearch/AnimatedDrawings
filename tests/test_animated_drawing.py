# Copyright (c) Meta Platforms, Inc. and affiliates.

from animated_drawings.model.animated_drawing import AnimatedDrawing
import yaml
from pathlib import Path
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

    char_cfg_fn = resource_filename(__name__, 'test_files/char1/char_cfg.yaml')
    with open(char_cfg_fn, 'r') as f:
        char_cfg = yaml.load(f, Loader=yaml.FullLoader)
    char_cfg['char_files_dir'] = str(Path(char_cfg_fn).parent)

    motion_cfg_fn = resource_filename(__name__, 'test_files/zombie.yaml')
    with open(motion_cfg_fn, 'r') as f:
        motion_cfg = yaml.load(f, Loader=yaml.FullLoader)
    retarget_cfg_fn = resource_filename(__name__, 'test_files/human_zombie.yaml')
    with open(retarget_cfg_fn, 'r') as f:
        retarget_cfg = yaml.load(f, Loader=yaml.FullLoader)
    AnimatedDrawing(char_cfg, retarget_cfg, motion_cfg)

    assert True
