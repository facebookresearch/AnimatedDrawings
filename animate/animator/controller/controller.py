from animator.model.scene import Scene
from animator.view.view import View
from typing import Optional
from abc import abstractmethod


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
            self._handle_user_input()
            self._tick()
            self._update()
            self._render()
            self._finish_run_loop_iteration()
        
        self._cleanup_after_run_loop()
