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
    with open(f'{os.environ["AD_ROOT_DIR"]}/animate/config/scene_base_cfg.yaml', 'r') as f:
        base_cfg = defaultdict(dict, yaml.load(f, Loader=yaml.FullLoader))
    with open(user_cfg_fn, 'r') as f:
        user_cfg = defaultdict(dict, yaml.load(f, Loader=yaml.FullLoader) or {})
    cfg = defaultdict(dict, {**base_cfg, **user_cfg})
    cfg['controller'] = {**base_cfg['controller'], **user_cfg['controller']}
    cfg['view'] = {**base_cfg['view'], **user_cfg['view']}


    # create view
    if cfg['view']['USE_MESA']:
        from animator.view.mesa_view import MesaView
        view = MesaView(cfg['view'])
    else:
        from view.window_view import WindowView
        view = WindowView(cfg['view'])

    # create scene
    scene = Scene(cfg['scene'])

    # populate scene
    if cfg['DRAW_FLOOR']:
        from animator.model.floor import Floor
        scene.add_child(Floor())
    
    max_video_frames = 0
    video_fps = None
    # Add the Animated Drawing
    from animator.model.animated_drawing import AnimatedDrawing
    for ad_dict in cfg['ANIMATED_CHARACTERS']:
        with open(ad_dict['motion_cfg'], 'r') as f:
            motion_cfg = yaml.load(f, Loader=yaml.FullLoader)
        with open(ad_dict['retarget_cfg'], 'r') as f:
            retarget_cfg = yaml.load(f, Loader=yaml.FullLoader)
        with open(ad_dict['character_cfg'], 'r') as f:
            char_cfg = yaml.load(f, Loader=yaml.FullLoader)
            char_cfg['char_files_dir'] = str(Path(ad_dict['character_cfg']).parent)  # save the path so we can get image and mask from same directory

        # add the character
        ad = AnimatedDrawing(char_cfg, retarget_cfg, motion_cfg)
        scene.add_child(ad)
        if cfg['DRAW_AD_RETARGET_BVH']:
            scene.add_child(ad.retargeter.bvh)

        max_video_frames = max(max_video_frames, motion_cfg['end_frame_idx'] - motion_cfg['start_frame_idx'])
        if video_fps is None:
            video_fps = 1 / ad.retargeter.bvh.frame_time
        elif video_fps != 1 / ad.retargeter.bvh.frame_time:
            msg = 'BVH files with mismatching Frame Times in same scene. If using video, Frame Time of first BVH will be used'
            logging.info(msg)


    # create controller
    if cfg['controller']['MODE'] == 'video_render':
        # calculate the number of frames we'll be rendering
        video_frames = max_video_frames

        # save video to parent directory of user_cfg_fn
        out_dir = str(Path(user_cfg_fn).parent)

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

    user_cfg_fn = sys.argv[1]  # user-specified MVC configs
    bvh_metadata_cfg_fn = sys.argv[2]  # bvh-specific metadata config

    char_bvh_retargeting_cfg_fn = sys.argv[3]  # bvh->character retargeting config

    char_cfg_fn = sys.argv[4]  # character-specific config

    start(user_cfg_fn, bvh_metadata_cfg_fn, char_bvh_retargeting_cfg_fn, char_cfg_fn)