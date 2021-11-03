import yaml
import sys
import os
import logging
from pathlib import Path
from util import prep_render_backend


def build_scene_cfg():
    with open(sys.argv[1], 'r') as f:
        scene_cfg = yaml.load(f, Loader=yaml.FullLoader)

    with open('./config/base.yaml', 'r') as f:
        base_cfg = yaml.load(f, Loader=yaml.FullLoader)

    return {**base_cfg, **scene_cfg}  # combine and overwrite base with user specified config when necessary


def build_sketch_cfg():
    character_cfg_path = Path(sys.argv[2])
    with open(character_cfg_path, 'r') as f:
        sketch_cfg = yaml.load(f, Loader=yaml.FullLoader)

        sketch_cfg['image_loc'] = f"{str(character_cfg_path.parent)}/{sketch_cfg['image_name']}"

    return sketch_cfg


def main(scene_cfg, sketch_cfg):
    logging.info(f'RENDER_MODE is {scene_cfg["RENDER_MODE"]}')

    if scene_cfg['RENDER_MODE'] == 'RENDER':
        prep_render_backend()
        import SceneManager.render_manager as render_manager
        scene_manager = render_manager.RenderManager(cfg=scene_cfg)
    elif scene_cfg['RENDER_MODE'] == 'INTERACT':
        import SceneManager.interactive_manager as interactive_manager
        scene_manager = interactive_manager.InteractiveManager(cfg=scene_cfg)
    else:
        assert False, f'bad cfg["RENDER_MODE"]: {scene_cfg["RENDER_MODE"]}'

    from Shapes.ARAP_Sketch import ARAP_Sketch
    from Shapes.Floor import Floor
    from Shapes.BVH import BVH
    from camera import Camera
    from util import bodypart_groups

    # first add any background scene elements (depth test is disabled)
    if scene_cfg['DRAW_FLOOR']:
        scene_manager.add(Floor())

    # Create the ARAP_Sketch object (or unpickle if already exists), and add to scene
    ARAP_pickle_loc = os.path.join(Path(sketch_cfg['image_loc']).parent, 'ARAP_Sketch.pickle')
    if os.path.exists(ARAP_pickle_loc):
        print(f'pickled arap_sketch exists. Using it: {ARAP_pickle_loc}')
        arap_sketch = ARAP_Sketch.load_from_pickle(ARAP_pickle_loc)
    else:
        print(f'pickled arap_sketch DNE. Creating it: {ARAP_pickle_loc}')
        arap_sketch = ARAP_Sketch(sketch_cfg, scene_cfg)

    scene_manager.add_sketch(arap_sketch)

    if scene_cfg['RENDER_MODE'] == 'INTERACT':
        bvh = BVH(scene_cfg)
        scene_manager.add_bvh(bvh)
        scene_manager.create_root_motion_transferrer()
    else:
        scene_manager.create_transferrer_render()
        scene_manager.create_timemanager_render()

    # add all cameras
    for cam_cfg in scene_cfg['Cameras']:
        if cam_cfg['type'] == 'ignore':
            continue

        cam = Camera(scene_cfg, cam_cfg['cam_pos'], cam_cfg['cam_up'], yaw=cam_cfg['yaw'], name=cam_cfg['name'],
                     cam_type=cam_cfg['type'])

        if cam_cfg['type'] == 'free':
            scene_manager.add_free_camera(cam)
        elif cam_cfg['type'] == 'triangulation':
            scene_manager.add_info_camera(cam)
        elif cam_cfg['type'] == 'sketch':
            scene_manager.add_sketch_camera(cam)
        elif cam_cfg['type'] == 'bvh':
            if scene_cfg['RENDER_MODE'] == 'INTERACT':
                scene_manager.add_bvh_camera(cam, bodypart_groups[cam_cfg['retarget_bodypart_group']])
        else:
            assert False, 'Unsupported camera type. cam name: {} - cam type: {}'.format(cam_cfg['name'],
                                                                                        cam_cfg['type'])
    scene_manager.run()


if __name__ == '__main__':

    logging.basicConfig(filename='log.txt', level=logging.DEBUG)

    if not os.path.exists(sys.argv[1]):
        assert False, 'Cannot find motion_config: {}'.format(sys.argv[1])
    scene_cfg = build_scene_cfg()

    if not os.path.exists(sys.argv[2]):
        assert False, 'Cannot find sketch_config: {}'.format(sys.argv[2])
    sketch_cfg = build_sketch_cfg()

    if not os.path.exists(sys.argv[3]):
        assert False, 'Output directory does not exist: {}'.format(sys.argv[3])
    scene_cfg['OUTPUT_PATH'] = sys.argv[3]

    main(scene_cfg, sketch_cfg)
