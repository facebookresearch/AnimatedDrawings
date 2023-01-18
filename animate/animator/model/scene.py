from animator.model.transform import Transform
from animator.model.time_manager import TimeManager
import yaml
from pathlib import Path


class Scene(Transform, TimeManager):
    """
    The scene is the singular 'world' object.
    It contains all objects that need to be drawn.
    It keeps track of global time.
    """

    def __init__(self, cfg: dict):
        """ Takes in the scene dictionary from an mvc config file and prepares the scene. """
        super().__init__()

        # add floor if required
        if cfg['ADD_FLOOR']:
            from animator.model.floor import Floor
            self.add_child(Floor())

        # Add the Animated Drawing
        from animator.model.animated_drawing import AnimatedDrawing
        for ad_dict in cfg['ANIMATED_CHARACTERS']:
            with open(ad_dict['motion_cfg'], 'r') as f:
                motion_cfg = yaml.load(f, Loader=yaml.FullLoader)
            with open(ad_dict['retarget_cfg'], 'r') as f:
                retarget_cfg = yaml.load(f, Loader=yaml.FullLoader)
            with open(ad_dict['character_cfg'], 'r') as f:
                char_cfg = yaml.load(f, Loader=yaml.FullLoader)

            # save the path so we can get image and mask from same directory
            char_cfg['char_files_dir'] = str(Path(ad_dict['character_cfg']).parent)

            # add the character to the scene
            ad = AnimatedDrawing(char_cfg, retarget_cfg, motion_cfg)
            self.add_child(ad)
            if cfg['ADD_AD_RETARGET_BVH']:
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
