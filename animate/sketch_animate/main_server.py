import yaml
import os
import logging

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from util import prep_render_backend
prep_render_backend()

from Shapes.ARAP_Sketch import ARAP_Sketch
from Shapes.Floor import Floor
from camera import Camera
import SceneManager.render_manager as render_manager


def build_cfg(motion_cfg_path):
    with open('../sketch_animate/config/base.yaml', 'r') as f:
        base_cfg = yaml.load(f, Loader=yaml.FullLoader)

    with open(motion_cfg_path, 'r') as f:
        scene_cfg = yaml.load(f, Loader=yaml.FullLoader)

    logging.info(f'loaded scene_cfg: {motion_cfg_path}')

    return {**base_cfg, **scene_cfg}  # combine and overwrite base with user specified config when necessary


def video_from_cfg(sketch_cfg_path, motion_cfg_path, video_output_path):

    cfg = build_cfg(motion_cfg_path)

    cfg['OUTPUT_PATH'] = str(Path(video_output_path).resolve())

    scene_manager = render_manager.RenderManager(cfg=cfg)

    # first add any background scene elements (depth test is disabled)
    if cfg['DRAW_FLOOR']:
        scene_manager.add(Floor())

    # create character and add to scene
    sketch_cfg_path = Path(sketch_cfg_path)
    with open(sketch_cfg_path, 'r') as f:
        sketch_cfg = yaml.load(f, Loader=yaml.FullLoader)
        sketch_cfg['image_loc'] = f"{str(sketch_cfg_path.parent)}/{sketch_cfg['image_name']}"

    ARAP_pickle_loc = os.path.join(Path(sketch_cfg['image_loc']).parent, 'ARAP_Sketch.pickle')
    if os.path.exists(ARAP_pickle_loc):
        logging.info(f'pickled arap_sketch exists. Using it: {ARAP_pickle_loc}')
        arap_sketch = ARAP_Sketch.load_from_pickle(ARAP_pickle_loc)
    else:
        logging.info(f'pickled arap_sketch DNE. Creating it: {ARAP_pickle_loc}')
        arap_sketch = ARAP_Sketch(sketch_cfg, cfg)

    scene_manager.add_sketch(arap_sketch)

    # server will only run RENDER mode
    scene_manager.create_transferrer_render()
    scene_manager.create_timemanager_render()

    # add all cameras
    for cam_cfg in cfg['Cameras']:
        if cam_cfg['type'] == 'ignore':
            continue

        cam = Camera(cfg, cam_cfg['cam_pos'], cam_cfg['cam_up'], yaw=cam_cfg['yaw'], name=cam_cfg['name'],
                     cam_type=cam_cfg['type'])

        if cam_cfg['type'] == 'free':
            scene_manager.add_free_camera(cam)
        elif cam_cfg['type'] == 'triangulation':
            scene_manager.add_info_camera(cam)
        elif cam_cfg['type'] == 'sketch':
            scene_manager.add_sketch_camera(cam)
        elif cam_cfg['type'] == 'bvh':
            pass # server will only run RENDER mode, no bvh cam needed
        else:
            assert False, 'Unsupported camera type. cam name: {} - cam type: {}'.format(cam_cfg['name'],
                                                                                        cam_cfg['type'])
    scene_manager.run()


if __name__ == '__main__':
    if not os.path.exists(sys.argv[1]):
        assert False, 'Cannot find motion_config: {}'.format(sys.argv[1])

    if not os.path.exists(sys.argv[2]):
        assert False, 'Cannot find sketch_config: {}'.format(sys.argv[2])

    if not os.path.exists(sys.argv[3]):
        assert False, 'Output directory does not exist: {}'.format(sys.argv[3])

    logging.basicConfig(filename='log.txt', level=logging.DEBUG)
    video_from_cfg(sys.argv[2], sys.argv[1], sys.argv[3])
