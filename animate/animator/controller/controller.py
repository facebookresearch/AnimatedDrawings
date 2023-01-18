from __future__ import annotations
from animator.model.scene import Scene
from animator.view.view import View
from typing import Optional
from abc import abstractmethod
import logging

class Controller():
    """
    Base Controller class from which all other Controllers be be derived.
    Controllers are responsible for:
        - running the game loop.
        - handling user input and forwarding it to the view or scene.
        - triggering the scene's update method
        - trigger the view's render method
    """

    def __init__(self, cfg: dict, scene: Scene):
        self.cfg: dict = cfg
        self.scene: Scene = scene
        self.view: Optional[View] = None

    def set_scene(self, scene: Scene):
        self.scene = scene

    def set_view(self, view: View):
        self.view = view

    @abstractmethod
    def _tick(self):
        """Subclass and add logic is necessary to progress time"""
        pass

    @abstractmethod
    def _update(self):
        """Subclass and add logic is necessary to update scene after progressing time"""
        pass

    @abstractmethod
    def _is_run_over(self):
        """Subclass and add logic is necessary to end the scene"""
        pass

    @abstractmethod
    def _start_run_loop_iteration(self):
        """Subclass and add code to start run loop iteration"""
        pass

    @abstractmethod
    def _handle_user_input(self):
        """Subclass and add code to handle user input"""
        pass

    @abstractmethod
    def _render(self):
        """Subclass and add logic needed to have viewer render the scene"""
        pass

    @abstractmethod
    def _finish_run_loop_iteration(self):
        """Subclass and add steps necessary before starting next iteration of run loop. """
        pass

    @abstractmethod
    def _prep_for_run_loop(self):
        """Subclass and add anything necessary to do immediately prior to run loop. """
        pass

    @abstractmethod
    def _cleanup_after_run_loop(self):
        """Subclass and add anything necessary to do after run loop has finished. """
        pass

    def run(self):
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
    def create_controller(controller_cfg: dict, scene: Scene, view: View) -> Controller:
        """ Takes in a controller dictionary from MVC config, scene, and view. Constructs and return appropriate controller."""
        if controller_cfg['MODE'] == 'video_render':
            from controller.video_render_controller import VideoRenderController
            return VideoRenderController(controller_cfg, scene, view,)
        elif controller_cfg['MODE'] == 'interactive':
            from animator.controller.interactive_controller import InteractiveController
            return InteractiveController(controller_cfg, scene, view)
        else:
            msg = f'Unknown controller mode specified: {controller_cfg["MODE"]}'
            logging.critical(msg)
            assert False, msg