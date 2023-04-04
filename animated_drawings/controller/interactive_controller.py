# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

""" Interactive Controller Class Module """

import time
from typing import Optional
import glfw

from animated_drawings.controller.controller import Controller
from animated_drawings.model.scene import Scene
from animated_drawings.view.window_view import WindowView
from animated_drawings.config import ControllerConfig


class InteractiveController(Controller):
    """ Interactive Controller Class """

    def __init__(self, cfg: ControllerConfig, scene: Scene, view: WindowView) -> None:
        super().__init__(cfg, scene)

        self.view: WindowView = view
        self.prev_time: float = 0.0  # tracks real-world time passing between run loops
        self.pause: bool = False     # tracks whether time progresses in the scene

        glfw.init()
        glfw.set_key_callback(self.view.win, self._on_key)

    def _on_key(self, _win, key: int, _scancode, action, _mods) -> None:  # noqa: C901

        if action not in (glfw.PRESS, glfw.REPEAT):
            return

        # close window
        if key in (glfw.KEY_ESCAPE, glfw.KEY_Q):
            glfw.set_window_should_close(self.view.win, True)

        # move camera forward
        elif key == glfw.KEY_W:
            _, _, fwd = self.view.camera.get_right_up_fwd_vectors()
            self.view.camera.offset(-0.1 * fwd)

        # move camera back
        elif key == glfw.KEY_S:
            _, _, fwd = self.view.camera.get_right_up_fwd_vectors()
            self.view.camera.offset(0.1 * fwd)

        # move camera right
        elif key == glfw.KEY_A:
            right, _, _ = self.view.camera.get_right_up_fwd_vectors()
            self.view.camera.offset(-0.1 * right)

        # move camera left
        elif key == glfw.KEY_D:
            right, _, _ = self.view.camera.get_right_up_fwd_vectors()
            self.view.camera.offset(0.1 * right)

        # move camera up
        elif key == glfw.KEY_E:
            _, up, _ = self.view.camera.get_right_up_fwd_vectors()
            self.view.camera.offset(0.1 * up)

        # move camera down
        elif key == glfw.KEY_R:
            _, up, _ = self.view.camera.get_right_up_fwd_vectors()
            self.view.camera.offset(-0.1 * up)

        # toggle start/stop time
        elif key == glfw.KEY_SPACE:
            self.pause = not self.pause
            self.prev_time = time.time()

        # step forward in time
        elif key == glfw.KEY_RIGHT:
            self._tick(self.cfg.keyboard_timestep)

        # step backward in time
        elif key == glfw.KEY_LEFT:
            self._tick(-self.cfg.keyboard_timestep)

    def _is_run_over(self) -> None:
        return glfw.window_should_close(self.view.win)

    def _prep_for_run_loop(self) -> None:
        self.prev_time = time.time()

    def _start_run_loop_iteration(self) -> None:
        self.view.clear_window()

    def _tick(self, delta_t: Optional[float] = None) -> None:
        # if passed a specific value to progress time by, do so
        if delta_t:
            self.scene.progress_time(delta_t)
        # otherwise, if scene is paused, do nothing
        elif self.pause:
            pass
        # otherwise, calculate real time passed since last call and progress scene by that amount
        else:
            cur_time = time.time()
            self.scene.progress_time(cur_time - self.prev_time)
            self.prev_time = cur_time

    def _update(self) -> None:
        self.scene.update_transforms()

    def _handle_user_input(self) -> None:
        glfw.poll_events()

    def _render(self) -> None:
        self.view.render(self.scene)

    def _finish_run_loop_iteration(self) -> None:
        self.view.swap_buffers()

    def _cleanup_after_run_loop(self) -> None:
        self.view.cleanup()
