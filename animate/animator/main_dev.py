from animator.model.scene import Scene
from animator.model.camera import Camera
from animator.controller.interactive_controller import InteractiveController
from animator.view.interactive_view import InteractiveView
from model.vector import Vector
from model.box import Box
import logging
import yaml


def get_cfg():
    with open('./config/base.yaml', 'r') as f:
        base_cfg = yaml.load(f, Loader=yaml.FullLoader)
        user_cfg = {}
        return {**base_cfg, **user_cfg}  # scene_cfg is base overwitten by user


cfg = get_cfg()
logging.basicConfig(filename='log.txt', level=logging.DEBUG)

if True:  # for interactive
    # TODO: Fix this once we move the shader code into view
    import glfw
    glfw.init()
    view_camera = Camera(pos=Vector(0.0, 0.0, -10))
    view = InteractiveView(cfg, view_camera)

scene = Scene(cfg)
view.set_scene(scene)

if True:  # for interactive
    # move glfw.init() here after shader code moved:w

    scene.add_child(view_camera)

    controller = InteractiveController(cfg, scene, view)

# Anything that calls OpenGL code needs to go down here:

box = Box()
scene.add_child(box)
controller.run()
