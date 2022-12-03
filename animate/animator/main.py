import yaml
import sys
import os
import logging
from pathlib import Path


def get_scene_cfg():
    try:
        with open(sys.argv[1], 'r') as f:
            user_cfg = yaml.load(f, Loader=yaml.FullLoader)
        with open('./config/base.yaml', 'r') as f:
            base_cfg = yaml.load(f, Loader=yaml.FullLoader)
        return {**base_cfg, **user_cfg}  # scene_cfg is base overwitten by user
    except Exception as e:
        logging.critical(f'Error building scene_cfg: {str(e)}')
        assert False


def get_sketch_cfg():
    try:
        character_cfg_path = Path(sys.argv[2])
        with open(character_cfg_path, 'r') as f:
            sketch_cfg = yaml.load(f, Loader=yaml.FullLoader)
        sketch_cfg['image_loc'] = f"{character_cfg_path.parent /character_cfg_path.stem}.png"
        return sketch_cfg
    except Exception as e:
        logging.critical(f'Error building sketch_cfg: {str(e)}')
        assert False


def get_scene_manager(scene_cfg):
    render_mode = scene_cfg["RENDER_MODE"]
    logging.info(f'RENDER_MODE is {render_mode}')
    if render_mode == 'RENDER':
        from sketch_animate.util import prep_render_backend
        from sketch_animate.SceneManager.render_manager import RenderManager
        prep_render_backend()
        return RenderManager(cfg=scene_cfg)
    elif render_mode == 'INTERACT':
        from sketch_animate.SceneManager.interactive_manager import InteractiveManager
        return InteractiveManager(cfg=scene_cfg)
    else:
        logging.critical(f'bad render_mode: {render_mode}')
        assert False


def main(scene_cfg, sketch_cfg):

    scene_manager = get_scene_manager(scene_cfg)

    # first add any background scene elements (depth test is disabled)
    if scene_cfg['DRAW_FLOOR']:
        from sketch_animate.Shapes.Floor import Floor
        scene_manager.add(Floor())

    # TODO: Hook to add background image to animation
    if 'DRAW_BACKGROUND' in scene_cfg.keys():
        pass

    # Add the character to the scene
    logging.info('Creating arap_sketch')
    from sketch_animate.Shapes.ARAP_Sketch import ARAP_Sketch
    arap_sketch = ARAP_Sketch(sketch_cfg, scene_cfg)
    scene_manager.add_sketch(arap_sketch)

    # if it's an interactive scene, we calculate the character's bone angles given the bvh
    # and the bvh cameras.
    # TODO: Remove this functionality.
    if scene_cfg['RENDER_MODE'] == 'INTERACT':
        from sketch_animate.Shapes.BVH import BVH
        bvh = BVH(scene_cfg)
        scene_manager.add_bvh(bvh)
        scene_manager.create_root_motion_transferrer()
    else:
        scene_manager.create_transferrer_render()
        scene_manager.create_timemanager_render()

    # add all cameras
    # TODO: Consider removing this. We only need a single camera, the 'free' camera
    from sketch_animate.camera import Camera
    from sketch_animate.util import bodypart_groups
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
                scene_manager.add_bvh_camera(
                    cam, bodypart_groups[cam_cfg['retarget_bodypart_group']])
        else:
            assert False, 'Unsupported camera type. cam name: {} - cam type: {}'.format(cam_cfg['name'],
                                                                                        cam_cfg['type'])
    scene_manager.run()


if __name__ == '__main__':

    logging.basicConfig(filename='log.txt', level=logging.DEBUG)

    scene_cfg = get_scene_cfg()

    sketch_cfg = get_sketch_cfg()

    if not os.path.exists(sys.argv[3]):
        assert False, 'Output directory does not exist: {}'.format(sys.argv[3])
    scene_cfg['OUTPUT_PATH'] = sys.argv[3]

    main(scene_cfg, sketch_cfg)
