from animator.model.scene import Scene
from animator.view.view import View
import logging
import yaml
import sys
from collections import defaultdict
from pathlib import Path
import os


def _build_config(user_cfg_fn: str) -> defaultdict:
    """ Combines and returns user-specified config file with base config file."""

    # ensure project root dir set as env var
    if 'AD_ROOT_DIR' not in os.environ:
        msg = 'AD_ROOT_DIR environmental variable not set'
        logging.critical(msg)
        assert False, msg

    # create the MVC config by combining base with user-specified options
    with open(f'{Path(os.environ["AD_ROOT_DIR"],"animate/animator/scene_base_cfg.yaml")}', 'r') as f:
        base_cfg = defaultdict(dict, yaml.load(f, Loader=yaml.FullLoader))
    with open(user_cfg_fn, 'r') as f:
        user_cfg = defaultdict(dict, yaml.load(f, Loader=yaml.FullLoader) or {})

    cfg = defaultdict(dict)
    cfg['scene'] = {**base_cfg['scene'], **user_cfg['scene']}
    cfg['controller'] = {**base_cfg['controller'], **user_cfg['controller']}
    cfg['view'] = {**base_cfg['view'], **user_cfg['view']}

    return cfg


def start(user_cfg_fn: str):

    # build cfg
    cfg = _build_config(user_cfg_fn)

    # create view
    view = View.create_view(cfg['view'])

    # create scene
    scene = Scene(cfg['scene'])

    # create controller
    if cfg['controller']['MODE'] == 'video_render':
        # calculate the number of frames we'll be rendering
        video_frames = max_video_frames

        # save video to parent directory of user_cfg_fn
        out_dir = cfg['controller']['OUTPUT_VIDEO_PATH']

        from controller.video_render_controller import VideoRenderController
        controller = VideoRenderController(cfg['controller'], scene, view, video_fps, video_frames, out_dir)
    elif cfg['controller']['MODE'] == 'interactive':
        from animator.controller.interactive_controller import InteractiveController
        controller = InteractiveController(cfg['controller'], scene, view)
    else:
        msg = f'Unknown controller type specified: {cfg["controller"]["type"]}'
        logging.critical(msg)
        assert False, msg
    # start the run loop
    controller.run()


if __name__ == '__main__':
    logging.basicConfig(filename='log.txt', level=logging.DEBUG)

    # user-specified scene-level configuration filepath
    scene_cfg_fn = sys.argv[1]

    start(scene_cfg_fn)