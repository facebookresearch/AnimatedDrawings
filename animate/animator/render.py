from animator.model.scene import Scene
from animator.view.view import View
from animator.controller.controller import Controller
import logging
import yaml
import sys
from collections import defaultdict
from pathlib import Path
import os


def _build_config(user_mvc_cfg_fn: str) -> defaultdict:
    """ Combines and returns user-specified config file with base config file."""

    # ensure project root dir set as env var
    if 'AD_ROOT_DIR' not in os.environ:
        msg = 'AD_ROOT_DIR environmental variable not set'
        logging.critical(msg)
        assert False, msg

    # create the MVC config by combining base with user-specified options
    with open(f'{Path(os.environ["AD_ROOT_DIR"],"animate/animator/scene_base_cfg.yaml")}', 'r') as f:
        base_cfg = defaultdict(dict, yaml.load(f, Loader=yaml.FullLoader))
    with open(user_mvc_cfg_fn, 'r') as f:
        user_cfg = defaultdict(dict, yaml.load(f, Loader=yaml.FullLoader) or {})

    cfg = defaultdict(dict)
    cfg['scene'] = {**base_cfg['scene'], **user_cfg['scene']}
    cfg['controller'] = {**base_cfg['controller'], **user_cfg['controller']}
    cfg['view'] = {**base_cfg['view'], **user_cfg['view']}

    return cfg


def start(user_mvc_cfg_fn: str):

    # build cfg
    cfg = _build_config(user_mvc_cfg_fn)

    # create view
    view = View.create_view(cfg['view'])

    # create scene
    scene = Scene(cfg['scene'])

    # create controller
    controller = Controller.create_controller(cfg['controller'], scene, view)

    # start the run loop
    controller.run()


if __name__ == '__main__':
    logging.basicConfig(filename='log.txt', level=logging.DEBUG)

    # user-specified mvc configuration filepath
    user_mvc_cfg_fn = sys.argv[1]

    start(user_mvc_cfg_fn)
