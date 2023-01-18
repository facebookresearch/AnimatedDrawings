from animator.model.scene import Scene
from animator.view.view import View
from animator.controller.controller import Controller
from animator.utils import resolve_ad_filepath
import logging
import yaml
import sys
from collections import defaultdict
from pathlib import Path
import os


def _build_config(user_mvc_cfg_fn: str) -> defaultdict:
    """ Combines and returns user-specified config file with base config file. """

    # prep the mvc base config
    with open(f'{Path(os.environ["AD_ROOT_DIR"],"animate/animator/mvc_base_cfg.yaml")}', 'r') as f:
        base_cfg = defaultdict(dict, yaml.load(f, Loader=yaml.FullLoader))

    # search for the user-specified mvc confing
    user_mvc_cfg_p: Path = resolve_ad_filepath(user_mvc_cfg_fn, 'user mvc config')
    logging.info(f'Using user-specified mvc config file located at {user_mvc_cfg_p.resolve()}')

    with open(str(user_mvc_cfg_p), 'r') as f:
        user_cfg = defaultdict(dict, yaml.load(f, Loader=yaml.FullLoader) or {})

    # build and return config dict
    cfg = defaultdict(dict)
    cfg['scene'] = {**base_cfg['scene'], **user_cfg['scene']}
    cfg['controller'] = {**base_cfg['controller'], **user_cfg['controller']}
    cfg['view'] = {**base_cfg['view'], **user_cfg['view']}
    return cfg


def start(user_mvc_cfg_fn: str):

    # ensure project root dir set as env var
    if 'AD_ROOT_DIR' not in os.environ:
        msg = 'AD_ROOT_DIR environmental variable not set'
        logging.critical(msg)
        assert False, msg

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

    # user-specified mvc configuration filepath. Can be absolute, relative to cwd, or relative to ${AD_ROOT_DIR}
    user_mvc_cfg_fn = sys.argv[1]

    start(user_mvc_cfg_fn)
