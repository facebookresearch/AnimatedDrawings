import glfw
from animator.controller.controller import Controller
from animator.model.scene import Scene
from animator.view.interactive_view import InteractiveView
from model.bvh import BVH
from typing import Optional


class InteractiveController(Controller):

    def __init__(self, cfg: dict, scene: Scene, view: InteractiveView):
        super().__init__(cfg, scene)

        self.view: InteractiveView = view

        self.bvh: Optional[BVH] = None

        glfw.set_key_callback(self.view.win, self._on_key)
        glfw.set_cursor_pos_callback(self.view.win, self._on_mouse_move)
        glfw.set_input_mode(self.view.win, glfw.CURSOR, glfw.CURSOR_DISABLED)

    def attach_view(self, view: InteractiveView):
        self.view = view

    def set_bvh(self, bvh: BVH):
        self.bvh = bvh

    def _on_key(self, _win, key: int, _scancode, action, _mods):
        if not (action == glfw.PRESS or action == glfw.REPEAT):
            return

        if key == glfw.KEY_ESCAPE or key == glfw.KEY_Q:
            glfw.set_window_should_close(self.view.win, True)

    def _on_mouse_move(self, win, xpos: float, ypos: float):
        pass

    def _is_run_over(self):
        return glfw.window_should_close(self.view.win)

    def _start_run_loop(self):
        self.view.clear_window()

        if self.bvh:
            self.bvh.cur_frame = (self.bvh.cur_frame + 1) % self.bvh.frame_num
            self.bvh.apply_frame(self.bvh.cur_frame)

        self.scene.update_transforms()

    def _handle_user_input(self):
        glfw.poll_events()

    def _render(self):
        self.view.render(self.scene)

    def _finish_run_loop(self):
        self.view.swap_buffers()
