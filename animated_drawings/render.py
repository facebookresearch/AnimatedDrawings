# Copyright (c) Meta Platforms, Inc. and affiliates.

from animated_drawings.model.scene import Scene
from animated_drawings.view.view import View
from animated_drawings.controller.controller import Controller
from animated_drawings.utils import resolve_ad_filepath
from animated_drawings.config import Config
import logging
import yaml
import sys
from collections import defaultdict
from pathlib import Path


def start(user_mvc_cfg_fn: str):

    # build cfg
    cfg: Config = Config(user_mvc_cfg_fn)

    # create view
    view = View.create_view(cfg.view)

    # create scene
    scene = Scene(cfg.scene)

    # create controller
    controller = Controller.create_controller(cfg.controller, scene, view)

    # start the run loop
    controller.run()


if __name__ == '__main__':
    logging.basicConfig(filename='log.txt', level=logging.DEBUG)

    # user-specified mvc configuration filepath. Can be absolute, relative to cwd, or relative to ${AD_ROOT_DIR}
    user_mvc_cfg_fn = sys.argv[1]

    start(user_mvc_cfg_fn)
