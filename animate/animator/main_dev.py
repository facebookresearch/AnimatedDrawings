from animator.model.scene import Scene
from animator.model.camera import Camera
from animator.model.animated_drawing import AnimatedDrawing
from animator.controller.interactive_controller import InteractiveController
from animator.view.interactive_view import InteractiveView
from model.vectors import Vectors
import logging
import yaml


def get_cfg():
    with open('./config/base.yaml', 'r') as f:
        base_cfg = yaml.load(f, Loader=yaml.FullLoader)
        user_cfg = {}
        return {**base_cfg, **user_cfg}  # scene_cfg is base overwitten by user


if __name__ == '__main__':
    logging.basicConfig(filename='log.txt', level=logging.DEBUG)

    cfg = get_cfg()

    scene = Scene(cfg)

    if True:  # code specific to running in 'interactive' mode
        import glfw
        glfw.init()

        view_camera = Camera(pos=Vectors([-0.5, -0.5, -3.0]), fwd=Vectors([0.0, 0.0, 1.0]))
        scene.add_child(view_camera)
        view = InteractiveView(cfg, view_camera)

        controller = InteractiveController(cfg, scene, view)

    ad = AnimatedDrawing('tests/test_character/nick_cat.yaml')
    scene.add_child(ad)

    controller.run()
