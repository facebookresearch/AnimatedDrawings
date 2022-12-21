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

        self.rotation = 0

    def attach_view(self, view: InteractiveView):
        self.view = view

    def set_bvh(self, bvh: BVH):
        self.bvh = bvh

    def _on_key(self, _win, key: int, _scancode, action, _mods):
        if not (action == glfw.PRESS or action == glfw.REPEAT):
            return

        if key == glfw.KEY_ESCAPE or key == glfw.KEY_Q:
            glfw.set_window_should_close(self.view.win, True)
        elif key == glfw.KEY_W:  # move camera forward
            fwd = self.view.camera.world_transform[:-1, 2]
            self.view.camera.offset(0.1 * fwd)
            self.view.camera
        elif key == glfw.KEY_S:  # move camera back
            fwd = self.view.camera.world_transform[:-1, 2]
            self.view.camera.offset(-0.1 * fwd)
            self.view.camera
        elif key == glfw.KEY_A:  # move camera right
            right = self.view.camera.world_transform[:-1, 0]
            self.view.camera.offset(0.1 * right)
            self.view.camera
        elif key == glfw.KEY_D:  # move camera left
            right = self.view.camera.world_transform[:-1, 0]
            self.view.camera.offset(-0.1 * right)
            self.view.camera
        elif key == glfw.KEY_E:  # move camera up
            up = self.view.camera.world_transform[:-1, 1]
            self.view.camera.offset(0.1 * up)
            self.view.camera
        elif key == glfw.KEY_R:  # move camera down
            up = self.view.camera.world_transform[:-1, 1]
            self.view.camera.offset(-0.1 * up)
            self.view.camera

    def _on_mouse_move(self, win, xpos: float, ypos: float):
        pass

    def _is_run_over(self):
        return glfw.window_should_close(self.view.win)

    def _start_run_loop_iteration(self):
        self.view.clear_window()

        self.scene.update_transforms()

    def _handle_user_input(self):
        glfw.poll_events()

    def _render(self):
        self.view.render(self.scene)

    def _finish_run_loop_iteration(self):
        self.view.swap_buffers()
