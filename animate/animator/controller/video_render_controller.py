from animator.controller.controller import Controller
from animator.model.scene import Scene
from animator.view.view import View
import time
import cv2
from OpenGL import GL
import numpy as np
import logging
from pathlib import Path
from typing import Tuple


class VideoRenderController(Controller):

    def __init__(self, cfg: dict, scene: Scene, view: View):
        super().__init__(cfg, scene)

        self.view: View = view

        self.scene: Scene = scene

        self.frames_left_to_render: int  # when this becomes zero, stop rendering
        self.delta_t: float  # amount of time to progress scene between renders
        self.frames_left_to_render, self.delta_t = self._get_max_motion_frames_and_frame_time()

        self.video_width: int
        self.video_height: int
        self.video_writer: cv2.VideoWriter
        self._initialize_video_writer()

        self.frame_data = np.empty([self.video_height, self.video_width, 4], dtype='uint8')  # 4 for RGBA
        self.frames_rendered = 0

    def _get_max_motion_frames_and_frame_time(self) -> Tuple[int, float]:
        """
        Based upon the animated drawings within the scene, computes maximum number of frames in a BVH.
        Checks that all frame times within BVHs are equal, logs a warning if not.
        Return max number of BVH frames and frame time of first BVH.
        """

        max_frames = 0
        frame_time = []
        for child in self.scene.get_children():
            try:
                max_frames = max(max_frames, child.retargeter.bvh.frame_max_num)
                frame_time.append(child.retargeter.bvh.frame_time)
            except AttributeError:
                pass  # child wasn't an Animated Drawing. Fine to skip it
            except Exception as e:
                msg = f'Error attempting to compute video max_frames and frame_time: {e}'
                logging.critical(msg)
                assert False, msg

        if not all(x == frame_time[0] for x in frame_time):
            msg = f'frame time of BVH files don\'t match. Using first value: {frame_time[0]}'
            logging.warning(msg)

        return max_frames, frame_time[0]

    def _initialize_video_writer(self) -> None:
        """ Logic necessary for setting up the video writer. """

        # prep video output location
        output_p = Path(self.cfg['OUTPUT_VIDEO_PATH'])
        output_p.parent.mkdir(exist_ok=True, parents=True)
        logging.info(f'Writing video to {output_p.resolve()}')

        # prep codec
        fourcc = cv2.VideoWriter_fourcc(*self.cfg['OUTPUT_VIDEO_CODEC'])
        logging.info(f'Using {self.cfg["OUTPUT_VIDEO_CODEC"]}')

        # prep video dimensions
        self.video_width, self.video_height = self.view.get_framebuffer_size()

        # initialize the video writer
        self.video_writer = cv2.VideoWriter(str(output_p), fourcc, 1 / self.delta_t, (self.video_width, self.video_height))

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
        self.frames_rendered += 1

    def _prep_for_run_loop(self):
        self.start_time = time.time()

    def _cleanup_after_run_loop(self):
        logging.info(f'Rendered {self.frames_rendered} frames in {time.time()-self.start_time} seconds.')
        _time = time.time()
        self.video_writer.release()
        logging.info(f'Wrote video to file in in {time.time()-_time} seconds.')
