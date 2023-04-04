# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

""" Controller Abstract Base Class Module """

from __future__ import annotations
from typing import Optional
from abc import abstractmethod
import logging

from animated_drawings.model.scene import Scene
from animated_drawings.view.view import View
from animated_drawings.config import ControllerConfig


class Controller():
    """
    Base Controller class from which all other Controllers be be derived.
    Controllers are responsible for:
        - running the game loop.
        - handling user input and forwarding it to the view or scene.
        - triggering the scene's update method
        - trigger the view's render method
    """

    def __init__(self, cfg: ControllerConfig, scene: Scene) -> None:
        self.cfg: ControllerConfig = cfg
        self.scene: Scene = scene
        self.view: Optional[View] = None

    def set_scene(self, scene: Scene) -> None:
        """ Sets the scene attached to this controller."""
        self.scene = scene

    def set_view(self, view: View) -> None:
        """ Sets the view attached to this controller."""
        self.view = view

    @abstractmethod
    def _tick(self) -> None:
        """Subclass and add logic is necessary to progress time"""

    @abstractmethod
    def _update(self) -> None:
        """Subclass and add logic is necessary to update scene after progressing time"""

    @abstractmethod
    def _is_run_over(self) -> bool:
        """Subclass and add logic is necessary to end the scene"""

    @abstractmethod
    def _start_run_loop_iteration(self) -> None:
        """Subclass and add code to start run loop iteration"""

    @abstractmethod
    def _handle_user_input(self) -> None:
        """Subclass and add code to handle user input"""

    @abstractmethod
    def _render(self) -> None:
        """Subclass and add logic needed to have viewer render the scene"""

    @abstractmethod
    def _finish_run_loop_iteration(self) -> None:
        """Subclass and add steps necessary before starting next iteration of run loop. """

    @abstractmethod
    def _prep_for_run_loop(self) -> None:
        """Subclass and add anything necessary to do immediately prior to run loop. """

    @abstractmethod
    def _cleanup_after_run_loop(self) -> None:
        """Subclass and add anything necessary to do after run loop has finished. """

    def run(self) -> None:
        """ The run loop. Subclassed controllers should overload and define functionality for each step in this function."""

        self._prep_for_run_loop()
        while not self._is_run_over():
            self._start_run_loop_iteration()
            self._update()
            self._render()
            self._tick()
            self._handle_user_input()
            self._finish_run_loop_iteration()

        self._cleanup_after_run_loop()

    @staticmethod
    def create_controller(controller_cfg: ControllerConfig, scene: Scene, view: View) -> Controller:
        """ Takes in a controller dictionary from mvc config file, scene, and view. Constructs and return appropriate controller."""
        if controller_cfg.mode == 'video_render':
            from animated_drawings.controller.video_render_controller import VideoRenderController
            return VideoRenderController(controller_cfg, scene, view,)
        elif controller_cfg.mode == 'interactive':
            from animated_drawings.controller.interactive_controller import InteractiveController
            from animated_drawings.view.window_view import WindowView
            assert isinstance(view, WindowView)  # for static analysis. checks elsewhere ensure this always passes
            return InteractiveController(controller_cfg, scene, view)
        else:
            msg = f'Unknown controller mode specified: {controller_cfg.mode}'
            logging.critical(msg)
            assert False, msg
