from image_to_annotations import image_to_annotations
from pathlib import Path
import animator.render
import logging
import sys
import os


def image_to_animation(img_fn: str, out_dir: str,  user_cfg_fn: str, bvh_metadata_cfg_fn: str, char_bvh_retargeting_cfg_fn: str):
    """
    Given the image located at img_fn, run character detection, segmentation, and pose estimation on the character within it.
    Create an animation from it using the config files passed in TODO Expand on what each config does
    Saves the character files and the animation to out_dir
    """

    # create the annotations
    image_to_annotations(img_fn, out_dir)

    char_cfg_fn = f'{Path(out_dir)}/char_cfg.yaml'

    animator.render.start(user_cfg_fn, bvh_metadata_cfg_fn, char_bvh_retargeting_cfg_fn, char_cfg_fn)


if __name__ == '__main__':
    log_dir = Path('./logs')
    log_dir.mkdir(exist_ok=True, parents=True)
    logging.basicConfig(filename=f'{log_dir}/log.txt', level=logging.DEBUG)

    img_fn = sys.argv[1]
    out_dir = sys.argv[2]

    # TODO: Remove these hardcodings - only for development
    user_cfg_fn = f'{os.environ["AD_ROOT_DIR"]}/animate/config/user_cfg_windowed_video_export.yaml'
    # user_cfg_fn = f'{os.environ["AD_ROOT_DIR"]}'/animate/config/user_cfg_windowed_interactive.yaml'
    bvh_metadata_cfg_fn = f'{os.environ["AD_ROOT_DIR"]}/animate/config/dab_bvh_metadata_cfg.yml'
    char_bvh_retargeting_cfg_fn = f'{os.environ["AD_ROOT_DIR"]}/animate/config/char_bvh_retargeting_cfg.yml'
    image_to_animation(img_fn, out_dir, user_cfg_fn, bvh_metadata_cfg_fn, char_bvh_retargeting_cfg_fn)
