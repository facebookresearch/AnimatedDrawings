# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import animated_drawings.render
import logging
from pathlib import Path
import sys
import yaml
from pkg_resources import resource_filename


def annotations_to_animation(char_anno_dir: str, motion_cfg_fn: str, retarget_cfg_fn: str):
    """
    Given a path to a directory with character annotations, a motion configuration file, and a retarget configuration file,
    creates an animation and saves it to {annotation_dir}/video.png
    """

    # package character_cfg_fn, motion_cfg_fn, and retarget_cfg_fn
    animated_drawing_dict = {
        'character_cfg': str(Path(char_anno_dir, 'char_cfg.yaml').resolve()),
        'motion_cfg': str(Path(motion_cfg_fn).resolve()),
        'retarget_cfg': str(Path(retarget_cfg_fn).resolve())
    }

    # create mvc config
    mvc_cfg = {
        'scene': {'ANIMATED_CHARACTERS': [animated_drawing_dict]},  # add the character to the scene
        'controller': {
            'MODE': 'video_render',  # 'video_render' or 'interactive'
            'OUTPUT_VIDEO_PATH': str(Path(char_anno_dir, 'video.gif').resolve())}  # set the output location
    }

    # write the new mvc config file out
    output_mvc_cfn_fn = str(Path(char_anno_dir, 'mvc_cfg.yaml'))
    with open(output_mvc_cfn_fn, 'w') as f:
        yaml.dump(dict(mvc_cfg), f)

    # render the video
    animated_drawings.render.start(output_mvc_cfn_fn)


if __name__ == '__main__':

    log_dir = Path('./logs')
    log_dir.mkdir(exist_ok=True, parents=True)
    logging.basicConfig(filename=f'{log_dir}/log.txt', level=logging.DEBUG)

    char_anno_dir = sys.argv[1]
    if len(sys.argv) > 2:
        motion_cfg_fn = sys.argv[2]
    else:
        motion_cfg_fn = resource_filename(__name__, 'config/motion/dab.yaml')
    if len(sys.argv) > 3:
        retarget_cfg_fn = sys.argv[3]
    else:
        retarget_cfg_fn = resource_filename(__name__, 'config/retarget/fair1_ppf.yaml')

    annotations_to_animation(char_anno_dir, motion_cfg_fn, retarget_cfg_fn)
