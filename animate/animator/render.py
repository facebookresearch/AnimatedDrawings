from animator.model.scene import Scene
import logging
import yaml
import sys
from collections import defaultdict
from pathlib import Path
import os


def start(user_cfg_fn: str, bvh_metadata_cfg_fn: str, char_bvh_retargeting_cfg_fn: str, char_cfg_fn: str):

    # ensure project root dir set as env var
    if 'AD_ROOT_DIR' not in os.environ:
        msg = 'AD_ROOT_DIR environmental variable not set'
        logging.critical(msg)
        assert False, msg

    # create the MVC config by combining base with user-specified options
    with open(f'{os.environ["AD_ROOT_DIR"]}/animate/config/base_cfg.yaml', 'r') as f:
        base_cfg = defaultdict(dict, yaml.load(f, Loader=yaml.FullLoader))
    with open(user_cfg_fn, 'r') as f:
        user_cfg = defaultdict(dict, yaml.load(f, Loader=yaml.FullLoader) or {})
    cfg = defaultdict(dict, {**base_cfg, **user_cfg})
    cfg['controller'] = {**base_cfg['controller'], **user_cfg['controller']}
    cfg['view'] = {**base_cfg['view'], **user_cfg['view']}

    # get the configs needed for animation
    with open(bvh_metadata_cfg_fn, 'r') as f:
        bvh_metadata_cfg = yaml.load(f, Loader=yaml.FullLoader)
    with open(char_bvh_retargeting_cfg_fn, 'r') as f:
        char_bvh_retargeting_cfg = yaml.load(f, Loader=yaml.FullLoader)
    with open(char_cfg_fn, 'r') as f:
        char_cfg = yaml.load(f, Loader=yaml.FullLoader)
    char_cfg['char_files_dir'] = str(Path(char_cfg_fn).parent)  # save the path so we can get image and mask from same directory

    # create scene
    scene = Scene(cfg['scene'])

    # create view
    if cfg['view']['USE_MESA']:
        from animator.view.mesa_view import MesaView
        view = MesaView(cfg['view'])
    else:
        from animator.view.interactive_view import InteractiveView
        view = InteractiveView(cfg['view'])

    # create controller
    if cfg['controller']['type'] == 'video_render':
        from controller.video_render_controller import VideoRenderController
        video_fps = 1.0 / bvh_metadata_cfg['frame_time']
        video_frames = bvh_metadata_cfg['frames']
        out_dir = str(Path(char_cfg_fn).parent)
        controller = VideoRenderController(cfg['controller'], scene, view, video_fps, video_frames, out_dir)
    elif cfg['controller']['type'] == 'interactive':
        from animator.controller.interactive_controller import InteractiveController
        controller = InteractiveController(cfg['controller'], scene, view)
    else:
        msg = f'Unknown controller type specified: {cfg["controller"]["type"]}'
        logging.critical(msg)
        assert False, msg

    # populate scene
    if cfg['DRAW_FLOOR']:
        from animator.model.floor import Floor
        scene.add_child(Floor())
    
    # Add the Animated Drawing
    from animator.model.animated_drawing import AnimatedDrawing
    ad = AnimatedDrawing(char_cfg, char_bvh_retargeting_cfg, bvh_metadata_cfg)
    scene.add_child(ad)
    if cfg['DRAW_AD_RETARGET_BVH']:
        scene.add_child(ad.retargeter.bvh)

    # start the run loop
    controller.run()


if __name__ == '__main__':
    logging.basicConfig(filename='log.txt', level=logging.DEBUG)

    user_cfg_fn = sys.argv[1]  # user-specified MVC configs
    bvh_metadata_cfg_fn = sys.argv[2]  # bvh-specific metadata config

    char_bvh_retargeting_cfg_fn = sys.argv[3]  # bvh->character retargeting config

    char_cfg_fn = sys.argv[4]  # character-specific config

    start(user_cfg_fn, bvh_metadata_cfg_fn, char_bvh_retargeting_cfg_fn, char_cfg_fn)