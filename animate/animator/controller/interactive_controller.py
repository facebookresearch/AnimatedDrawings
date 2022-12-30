import glfw
from animator.controller.controller import Controller
from animator.model.scene import Scene
from animator.view.interactive_view import InteractiveView
#from model.bvh import BVH
from typing import Optional
import time

class InteractiveController(Controller):

    def __init__(self, cfg: dict, scene: Scene, view: InteractiveView):
        super().__init__(cfg, scene)

        self.view: InteractiveView = view

        self.prev_time: float = 0.0  # tracks real-world time passing between run loops. Set in _prep_for_run_loop

        glfw.set_key_callback(self.view.win, self._on_key)
        glfw.set_cursor_pos_callback(self.view.win, self._on_mouse_move)
        glfw.set_input_mode(self.view.win, glfw.CURSOR, glfw.CURSOR_DISABLED)

    def attach_view(self, view: InteractiveView):
        self.view = view

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

    def _on_mouse_move(self, win, xpos: float, ypos: float):
        pass

    def _is_run_over(self):
        return glfw.window_should_close(self.view.win)

    def _prep_for_run_loop(self):
        """ initialize time prior to beginning loop"""
        self.prev_time = time.time()

    def _start_run_loop_iteration(self):
        self.view.clear_window()

    def _tick(self):
        cur_time = time.time()
        delta_t: float = cur_time - self.prev_time
        self.prev_time = cur_time
        self.scene.progress_scene_time(delta_t)

    def _update(self):
        self.scene.update_transforms()

    def _handle_user_input(self):
        glfw.poll_events()

    def _render(self):
        self.view.render(self.scene)

    def _finish_run_loop_iteration(self):
        self.view.swap_buffers()
