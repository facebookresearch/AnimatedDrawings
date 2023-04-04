# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from animated_drawings.model.transform import Transform
from animated_drawings.model.time_manager import TimeManager
from animated_drawings.config import SceneConfig
from animated_drawings.model.floor import Floor
from animated_drawings.model.animated_drawing import AnimatedDrawing


class Scene(Transform, TimeManager):
    """
    The scene is the singular 'world' object.
    It contains all objects that need to be drawn.
    It keeps track of global time.
    """

    def __init__(self, cfg: SceneConfig) -> None:
        """ Takes in the scene dictionary from an mvc config file and prepares the scene. """
        super().__init__()

        # add floor if required
        if cfg.add_floor:
            self.add_child(Floor())

        # Add the Animated Drawings
        for each in cfg.animated_characters:

            ad = AnimatedDrawing(*each)
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
