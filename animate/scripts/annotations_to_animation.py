import animator.render
import logging
from pathlib import Path
import sys
import os

def annotations_to_animation(char_cfg_fn: str, user_cfg_fn: str, bvh_metadata_cfg_fn: str, char_bvh_retargeting_cfg_fn: str):
    """
    Given path to a character config file, (in the same format as output by image_to_annotation.py), animate the character in accordance with the passed in configuration files.
    `mask.png' and `texture.png' must also be present in the same directory as the character configuration file (although these could also be manually edited).
    If rendering a video, video saved to directory containing the character config file.
    Intended use-case: image_to_annotations.py failed to properly prep the character for animation, so you can manually adjust the annotations before using this function to generate the animation.
    """
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
    annotations_to_animation(img_fn, out_dir, user_cfg_fn, bvh_metadata_cfg_fn, char_bvh_retargeting_cfg_fn)