# Copyright (c) Meta Platforms, Inc. and affiliates.

import yaml
import logging
from animated_drawings.model.transform import Transform
from animated_drawings.model.time_manager import TimeManager
from animated_drawings.config import SceneConfig
from animated_drawings.model.floor import Floor
from animated_drawings.model.animated_drawing import AnimatedDrawing
from animated_drawings.utils import resolve_ad_filepath


class Scene(Transform, TimeManager):
    """
    The scene is the singular 'world' object.
    It contains all objects that need to be drawn.
    It keeps track of global time.
    """

    def __init__(self, cfg: SceneConfig):
        """ Takes in the scene dictionary from an mvc config file and prepares the scene. """
        super().__init__()

        # add floor if required
        if cfg.add_floor:
            self.add_child(Floor())

        # Add the Animated Drawings
        for each in cfg.animated_characters:

            # get filenames from config
            motion_cfg_fn: str = each['motion_cfg']
            retarget_cfg_fn: str = each['retarget_cfg']
            character_cfg_fn: str = each['character_cfg']

            # resolves paths
            motion_cfg_p = resolve_ad_filepath(motion_cfg_fn, 'motion cfg')
            retarget_cfg_p = resolve_ad_filepath(retarget_cfg_fn, 'retarget cfg')
            character_cfg_p = resolve_ad_filepath(character_cfg_fn, 'character cfg')

            # log what we're doing
            logging.info(f'Using motion_cfg located at {motion_cfg_p.resolve()}')
            logging.info(f'Using retarget_cfg located at {retarget_cfg_p.resolve()}')
            logging.info(f'Using character_cfg located at {character_cfg_p.resolve()}')

            # load the configs
            with open(str(motion_cfg_p), 'r') as f:
                motion_cfg = yaml.load(f, Loader=yaml.FullLoader)
            with open(str(retarget_cfg_p), 'r') as f:
                retarget_cfg = yaml.load(f, Loader=yaml.FullLoader)
            with open(str(character_cfg_p), 'r') as f:
                char_cfg = yaml.load(f, Loader=yaml.FullLoader)

            # save the path of parent dir so we can get image and mask from same directory
            char_cfg['char_files_dir'] = str(character_cfg_p.parent)

            # add the character to the scene
            ad = AnimatedDrawing(char_cfg, retarget_cfg, motion_cfg)
            self.add_child(ad)

            # add bvh to the scene if we're going to visualize it
            if cfg.add_ad_retarget_bvh:
                self.add_child(ad.retargeter.bvh)

    def progress_time(self, delta_t: float) -> None:
        """
        Entry point called to update time in the scene by delta_t seconds.
        Because animatable object within the scene may have their own individual timelines,
        we recurvisely go through objects in the scene and call tick() on each TimeManager.
        """
        self._progress_time(self, delta_t)

    def _progress_time(self, t: Transform, delta_t: float) -> None:
        """ Recursively calls tick() on all TimeManager objects. """

        if isinstance(t, TimeManager):
            t.tick(delta_t)

        for c in t.get_children():
            self._progress_time(c, delta_t)
