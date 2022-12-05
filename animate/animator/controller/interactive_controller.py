import glfw
from animator.controller.controller import Controller
from animator.model.scene import Scene
from animator.view.view import InteractiveView
import logging


class InteractiveController(Controller):

    def __init__(self, cfg: dict, scene: Scene, view: InteractiveView):
        super().__init__(cfg, scene)

        self.view: InteractiveView = view

        glfw.set_key_callback(self.view.win, self._on_key)
        glfw.set_cursor_pos_callback(self.view.win, self._on_mouse_move)
        glfw.set_input_mode(self.view.win, glfw.CURSOR, glfw.CURSOR_DISABLED)

    def _is_run_over(self):
        return glfw.window_should_close(self.view.win)

    def _prep_next_run_loop(self):
        self.view.swap_buffers()

    def _handle_user_input(self):
        glfw.poll_events()

    def _render(self):
        if self.view is None:
            logging.critical('Attempted to render but controller\'s view not set.')
            assert False

        # update shaders with camera's transform
        self.scene.update_shaders_view_transform(self.view.camera)
        self.view.render()

    def _on_key(self, _win, key: int, _scancode, action, _mods):

        if not (action == glfw.PRESS or action == glfw.REPEAT):
            return

        if key == glfw.KEY_ESCAPE or key == glfw.KEY_Q:
            glfw.set_window_should_close(self.view.win, True)

    def _on_mouse_move(self, win, xpos: float, ypos: float):
        pass

    def _start_of_run_loop(self):
        self.view.clear_window()
