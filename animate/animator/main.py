from animator.model.scene import Scene
from animator.model.camera import Camera
from animator.controller.interactive_controller import InteractiveController
from animator.view.interactive_view import InteractiveView
from animator.model.vectors import Vectors
from animator.model.animated_drawing import AnimatedDrawing
import logging
import yaml
from animator.model.floor import Floor
import glfw


if __name__ == '__main__':
    logging.basicConfig(filename='log.txt', level=logging.DEBUG)

    glfw.init()

    # cfg is base_cfg overwritten by user_cfg
    with open('./config/base_cfg.yaml', 'r') as f:
        base_cfg = yaml.load(f, Loader=yaml.FullLoader)
    with open('./config/user_cfg.yaml', 'r') as f:
        user_cfg = yaml.load(f, Loader=yaml.FullLoader) or {}
    cfg = {**base_cfg, **user_cfg}

    # create scene
    scene = Scene(cfg['scene'])

    # create view
    view_camera = Camera(pos=Vectors([0.0, 1.0, 5.0]), fwd=Vectors([0.0, 0.0, 1.0]))
    scene.add_child(view_camera)
    view = InteractiveView(cfg['view'], view_camera)

    # create controller
    controller = InteractiveController(cfg['controller'], scene, view)

    # add floor
    if cfg['DRAW_FLOOR']:
        scene.add_child(Floor())

    # create Animated Drawing character, position, add to scene
    with open('config/bvh_metadata_cfg.yml', 'r') as f:
        bvh_metadata_cfg = yaml.load(f, Loader=yaml.FullLoader)
    with open('config/char_bvh_retargeting_cfg.yml', 'r') as f:
        char_bvh_retargeting_cfg = yaml.load(f, Loader=yaml.FullLoader)
    with open('tests/test_character/nick_cat.yaml', 'r') as f:
        char_cfg = yaml.load(f, Loader=yaml.FullLoader)
    ad = AnimatedDrawing(char_cfg, char_bvh_retargeting_cfg, bvh_metadata_cfg)

    ad.offset(Vectors(cfg['CHARACTER_OFFSET']))

    scene.add_child(ad)

    # start the run loop
    controller.run()
