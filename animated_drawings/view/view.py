# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import annotations
from abc import abstractmethod
from typing import Tuple
from animated_drawings.config import ViewConfig


class View:
    """
    Base View class which all other Views must be derived.
    Views are responsible for controlling what is and isn't visible to them.
    Views are responsible for initiating the 'draw' methods for each object which they want to render.
    """

    def __init__(self, cfg: ViewConfig):
        self.cfg: ViewConfig = cfg
        pass

    @abstractmethod
    def render(self, scene) -> None:  # pyright: ignore[reportUnknownParameterType,reportMissingParameterType]
        """ Called by the controller to render the scene. """

    @abstractmethod
    def clear_window(self) -> None:
        """ Clear output from previous render loop. """

    @abstractmethod
    def cleanup(self) -> None:
        """ Cleanup after render loop is finished. """

    @abstractmethod
    def get_framebuffer_size(self) -> Tuple[int, int]:
        """ Return (width, height) of framebuffer. """

    @staticmethod
    def create_view(view_cfg: ViewConfig) -> View:
        """ Takes in a view dictionary from mvc config file and returns the appropriate view. """
        # create view
        if view_cfg.use_mesa:
            from animated_drawings.view.mesa_view import MesaView
            return MesaView(view_cfg)
        else:
            from animated_drawings.view.window_view import WindowView
            return WindowView(view_cfg)
