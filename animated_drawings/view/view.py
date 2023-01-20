from __future__ import annotations
from abc import abstractmethod
from typing import Tuple


class View:
    """
    Base View class which all other Views must be derived.
    Views are responsible for controlling what is and isn't visible to them.
    Views are responsible for initiating the 'draw' methods for each object which they want to render.
    """

    def __init__(self, cfg: dict):
        self.cfg: dict = cfg
        pass

    @abstractmethod
    def render(self, scene):
        """ Called by the controller to render the scene. """
        pass

    @abstractmethod
    def clear_window(self):
        """ Clear output from previous render loop. """
        pass

    @abstractmethod
    def cleanup(self):
        """ Cleanup after render loop is finished. """
        pass

    @abstractmethod
    def get_framebuffer_size(self) -> Tuple[int, int]:
        """ Return (width, height) of framebuffer. """
        pass

    @staticmethod
    def create_view(view_cfg: dict) -> View:
        """ Takes in a view dictionary from mvc config file and returns the appropriate view. """
        # create view
        if view_cfg['USE_MESA']:
            from animated_drawings.view.mesa_view import MesaView
            return MesaView(view_cfg)
        else:
            from animated_drawings.view.window_view import WindowView
            return WindowView(view_cfg)
