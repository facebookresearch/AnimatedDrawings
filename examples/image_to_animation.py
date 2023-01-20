from image_to_annotations import image_to_annotations
from pathlib import Path
import animated_drawings.render
import logging
import sys
import yaml
from collections import defaultdict
from pkg_resources import resource_filename

def image_to_animation(img_fn: str, out_dir: str,  mvc_cfg_fn: str, motion_cfg_fn: str, retarget_cfg_fn: str):
    """
    Given the image located at img_fn, run character detection, segmentation, and pose estimation on the character within it.
    Saves results to out_dir.
    Using the specified mvc_config_fn, renders an animation.
    """

    # create the annotations
    image_to_annotations(img_fn, out_dir)

    # combine character_cfg, motion_cfg, and retarget_cfg and add to scene
    animated_drawing_dict = {
            'character_cfg': str(Path(out_dir, 'char_cfg.yaml')),
            'motion_cfg': str(Path(motion_cfg_fn).resolve()),
            'retarget_cfg': str(Path(retarget_cfg_fn).resolve())
            }

    # open and read the mvc config file 
    with open(mvc_cfg_fn, 'r') as f:
        mvc_cfg = defaultdict(defaultdict, yaml.load(f, Loader=yaml.FullLoader) or {})
    
    # add the character to the scene
    mvc_cfg['scene']['ANIMATED_CHARACTERS'].append(animated_drawing_dict)

    # set the output directory
    mvc_cfg['controller']['OUTPUT_VIDEO_PATH'] = str(Path(out_dir, 'video.mp4'))

    # write the new mvc config file out
    output_mvc_cfn_fn = str(Path(out_dir, f'{Path(mvc_cfg_fn).stem}-{Path(img_fn).stem}.yaml'))
    with open(output_mvc_cfn_fn, 'w') as f:
        yaml.dump(dict(mvc_cfg), f)

    # render the video
    animated_drawings.render.start(output_mvc_cfn_fn)


if __name__ == '__main__':
    log_dir = Path('./logs')
    log_dir.mkdir(exist_ok=True, parents=True)
    logging.basicConfig(filename=f'{log_dir}/log.txt', level=logging.DEBUG)

    img_fn = sys.argv[1]
    out_dir = sys.argv[2]
    if len(sys.argv) > 3:
        mvc_cfg_fn = sys.argv[3]
    else:
        mvc_cfg_fn = resource_filename(__name__, 'config/mvc_window_video_export.yaml')
    if len(sys.argv) > 4:
        motion_cfg_fn = sys.argv[4]
    else:
        motion_cfg_fn = resource_filename(__name__, 'config/motion_dab.yaml')
    if len(sys.argv) > 5:
        retarget_cfg_fn = sys.argv[5]
    else:
        retarget_cfg_fn = resource_filename(__name__, 'config/retarget.yaml')


    # user_cfg_fn = f'{os.environ["AD_ROOT_DIR"]}/animate/config/user_cfg_windowed_video_export.yaml'
    image_to_animation(img_fn, out_dir, mvc_cfg_fn, motion_cfg_fn, retarget_cfg_fn)
