import glfw
from animated_drawings.controller.controller import Controller
from animated_drawings.model.scene import Scene
from animated_drawings.view.window_view import WindowView
from typing import Optional
import time


class InteractiveController(Controller):

    def __init__(self, cfg: dict, scene: Scene, view: WindowView):
        super().__init__(cfg, scene)

        self.view: WindowView = view
        self.prev_time: float = 0.0  # tracks real-world time passing between run loops.
        self.pause: bool = False  # does time progress?

        glfw.init()
        glfw.set_key_callback(self.view.win, self._on_key)
        glfw.set_cursor_pos_callback(self.view.win, self._on_mouse_move)
        glfw.set_input_mode(self.view.win, glfw.CURSOR, glfw.CURSOR_DISABLED)

    def _on_key(self, _win, key: int, _scancode, action, _mods):
        if not (action == glfw.PRESS or action == glfw.REPEAT):
            return

        if key == glfw.KEY_ESCAPE or key == glfw.KEY_Q:
            glfw.set_window_should_close(self.view.win, True)
        elif key == glfw.KEY_W:  # move camera forward
            _, _, fwd = self.view.camera.get_right_up_fwd_vectors()
            self.view.camera.offset(-0.1 * fwd)
            self.view.camera
        elif key == glfw.KEY_S:  # move camera back
            _, _, fwd = self.view.camera.get_right_up_fwd_vectors()
            self.view.camera.offset(0.1 * fwd)
            self.view.camera
        elif key == glfw.KEY_A:  # move camera right
            right, _, _ = self.view.camera.get_right_up_fwd_vectors()
            self.view.camera.offset(-0.1 * right)
            self.view.camera
        elif key == glfw.KEY_D:  # move camera left
            right, _, _ = self.view.camera.get_right_up_fwd_vectors()
            self.view.camera.offset(0.1 * right)
            self.view.camera
        elif key == glfw.KEY_E:  # move camera up
            _, up, _ = self.view.camera.get_right_up_fwd_vectors()
            self.view.camera.offset(0.1 * up)
            self.view.camera
        elif key == glfw.KEY_R:  # move camera down
            _, up, _ = self.view.camera.get_right_up_fwd_vectors()
            self.view.camera.offset(-0.1 * up)
            self.view.camera
        elif key == glfw.KEY_SPACE:  # toggle start/stop time
            self.pause = not self.pause
            self.prev_time = time.time()
        elif key == glfw.KEY_RIGHT:
            self._tick(self.cfg['KEYBOARD_TIMESTEP'])
        elif key == glfw.KEY_LEFT:
            self._tick(-self.cfg['KEYBOARD_TIMESTEP'])

    def _on_mouse_move(self, win, xpos: float, ypos: float):
        pass

    def _is_run_over(self):
        return glfw.window_should_close(self.view.win)

    def _prep_for_run_loop(self):
        """ initialize time prior to beginning loop"""
        self.prev_time = time.time()

    def _start_run_loop_iteration(self):
        self.view.clear_window()

    def _tick(self, delta_t: Optional[float] = None):
        """ If passed delta_t, advance scene by that amount of seconds. Otherwise, use elapsed real time since last _tick(). """
        if delta_t is None and self.pause:
            return

        cur_time = time.time()
        if delta_t is None:
            delta_t = cur_time - self.prev_time
        self.prev_time = cur_time

        self.scene.progress_time(delta_t)

    def _update(self):
        self.scene.update_transforms()

    def _handle_user_input(self):
        glfw.poll_events()

    def _render(self):
        self.view.render(self.scene)

    def _finish_run_loop_iteration(self):
        self.view.swap_buffers()

    def _cleanup_after_run_loop(self):
        self.view.cleanup()
