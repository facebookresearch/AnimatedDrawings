from animator.controller.controller import Controller
from animator.model.scene import Scene
from animator.view.view import View
import time
import cv2
from OpenGL import GL
import numpy as np
import logging
from pathlib import Path

class VideoRenderController(Controller):

    def __init__(self, cfg: dict, scene: Scene, view: View, video_fps: float, frames_to_render: int, output_path: str):
        super().__init__(cfg, scene)

        self.view: View = view

        self.scene: Scene = scene

        self.delta_t = 1.0 / video_fps  # amount to advance scene between rendering

        self.video_width: int
        self.video_height: int
        self.video_width, self.video_height = self.view.get_framebuffer_size()

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        if not output_path.endswith('.mp4'):
            msg = f'Only .mp4 output video files supported. Found {Path(output_path).suffix}'
            logging.critical(msg)
            assert False, msg

        self.video_writer = cv2.VideoWriter(output_path, fourcc, video_fps, (self.video_width, self.video_height))

        self.frame_data = np.empty([self.video_height, self.video_width, 4], dtype='uint8')  # 4 for RGBA
        self.frames = []
        self.frames_left_to_render = frames_to_render

    def _is_run_over(self):
        return self.frames_left_to_render == 0

    def _start_run_loop_iteration(self):
        self.view.clear_window()

    def _tick(self):
        self.scene.progress_time(self.delta_t)

    def _update(self):
        self.scene.update_transforms()

    def _render(self):
        self.view.render(self.scene)

        GL.glReadPixels(0, 0, self.video_height, self.video_width, GL.GL_BGRA, GL.GL_UNSIGNED_BYTE, self.frame_data)
        frame = self.frame_data[::-1, :, :3].copy()
        self.video_writer.write(frame)
        self.frames_left_to_render -= 1

    def _prep_for_run_loop(self):
        self.start_time = time.time()

    def _cleanup_after_run_loop(self):
        logging.info(f'Rendered {len(self.frames)} frames in {time.time()-self.start_time} seconds.')
        _time = time.time()
        self.video_writer.release()
        logging.info(f'Wrote video to file in in {time.time()-_time} seconds.')
