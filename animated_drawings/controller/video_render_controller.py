# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

""" Video Render Controller Class Module """

from __future__ import annotations
import time
import logging
from typing import List
from pathlib import Path
from abc import abstractmethod
import numpy as np
import numpy.typing as npt
import cv2
from OpenGL import GL
from tqdm import tqdm

from animated_drawings.controller.controller import Controller
from animated_drawings.model.scene import Scene
from animated_drawings.model.animated_drawing import AnimatedDrawing
from animated_drawings.view.view import View
from animated_drawings.config import ControllerConfig

NoneType = type(None)  # for type checking below


class VideoRenderController(Controller):
    """ Video Render Controller is used to non-interactively generate a video file """

    def __init__(self, cfg: ControllerConfig, scene: Scene, view: View) -> None:
        super().__init__(cfg, scene)

        self.view: View = view

        self.scene: Scene = scene

        self.frames_left_to_render: int  # when this becomes zero, stop rendering
        self.delta_t: float              # amount of time to progress scene between renders
        self._set_frames_left_to_render_and_delta_t()

        self.render_start_time: float  # track when we started to render frames (for performance stats)
        self.frames_rendered: int = 0  # track how many frames we've rendered

        self.video_width: int
        self.video_height: int
        self.video_width, self.video_height = self.view.get_framebuffer_size()

        self.video_writer: VideoWriter = VideoWriter.create_video_writer(self)

        self.frame_data = np.empty([self.video_height, self.video_width, 4], dtype='uint8')  # 4 for RGBA

        self.progress_bar = tqdm(total=self.frames_left_to_render)

    def _set_frames_left_to_render_and_delta_t(self) -> None:
        """
        Based upon the animated drawings within the scene, computes maximum number of frames in a BVH.
        Checks that all frame times within BVHs are equal, logs a warning if not.
        Uses results to determine number of frames and frame time for output video.
        """

        max_frames = 0
        frame_time: List[float] = []
        for child in self.scene.get_children():
            if not isinstance(child, AnimatedDrawing):
                continue
            max_frames = max(max_frames, child.retargeter.bvh.frame_max_num)
            frame_time.append(child.retargeter.bvh.frame_time)

        if not all(x == frame_time[0] for x in frame_time):
            msg = f'frame time of BVH files don\'t match. Using first value: {frame_time[0]}'
            logging.warning(msg)

        self.frames_left_to_render = max_frames
        self.delta_t = frame_time[0]

    def _prep_for_run_loop(self) -> None:
        self.run_loop_start_time = time.time()

    def _is_run_over(self) -> bool:
        return self.frames_left_to_render == 0

    def _start_run_loop_iteration(self) -> None:
        self.view.clear_window()

    def _update(self) -> None:
        self.scene.update_transforms()

    def _render(self) -> None:
        self.view.render(self.scene)

    def _tick(self) -> None:
        self.scene.progress_time(self.delta_t)

    def _handle_user_input(self) -> None:
        """ ignore all user input when rendering video file """

    def _finish_run_loop_iteration(self) -> None:
        # get pixel values from the frame buffer, send them to the video writer
        GL.glBindFramebuffer(GL.GL_READ_FRAMEBUFFER, 0)
        GL.glReadPixels(0, 0, self.video_width, self.video_height, GL.GL_BGRA, GL.GL_UNSIGNED_BYTE, self.frame_data)
        self.video_writer.process_frame(self.frame_data[::-1, :, :].copy())

        # update our counts and progress_bar
        self.frames_left_to_render -= 1
        self.frames_rendered += 1
        self.progress_bar.update(1)

    def _cleanup_after_run_loop(self) -> None:
        logging.info(f'Rendered {self.frames_rendered} frames in {time.time()-self.run_loop_start_time} seconds.')
        self.view.cleanup()

        _time = time.time()
        self.video_writer.cleanup()
        logging.info(f'Wrote video to file in in {time.time()-_time} seconds.')


class VideoWriter():
    """ Wrapper to abstract the different backends necessary for writing different video filetypes """

    def __init__(self) -> None:
        pass

    @abstractmethod
    def process_frame(self, frame: npt.NDArray[np.uint8]) -> None:
        """ Subclass must specify how to handle each frame of data received. """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """ Subclass must specify how to finish up after all frames have been received. """
        pass

    @staticmethod
    def create_video_writer(controller: VideoRenderController) -> VideoWriter:

        assert isinstance(controller.cfg.output_video_path, str)  # for static analysis

        output_p = Path(controller.cfg.output_video_path)
        output_p.parent.mkdir(exist_ok=True, parents=True)

        msg = f' Writing video to: {output_p.resolve()}'
        logging.info(msg)
        print(msg)

        if output_p.suffix == '.gif':
            return GIFWriter(controller)
        elif output_p.suffix == '.mp4':
            return MP4Writer(controller)
        else:
            msg = f'Unsupported output video file extension ({output_p.suffix}). Only .gif and .mp4 are supported.'
            logging.critical(msg)
            assert False, msg


class GIFWriter(VideoWriter):
    """ Video writer for creating transparent, animated GIFs with Pillow """

    def __init__(self, controller: VideoRenderController) -> None:
        assert isinstance(controller.cfg.output_video_path, str)  # for static analysis
        self.output_p = Path(controller.cfg.output_video_path)

        self.duration = int(controller.delta_t*1000)
        if self.duration < 20:
            msg = f'Specified duration of .gif is too low, replacing with 20: {self.duration}'
            logging.warn(msg)
            self.duration = 20

        self.frames: List[npt.NDArray[np.uint8]] = []

    def process_frame(self, frame: npt.NDArray[np.uint8]) -> None:
        """ Reorder channels and save frames as they arrive"""
        self.frames.append(cv2.cvtColor(frame, cv2.COLOR_BGRA2RGBA).astype(np.uint8))

    def cleanup(self) -> None:
        """ Write all frames to output path specified."""
        from PIL import Image
        self.output_p.parent.mkdir(exist_ok=True, parents=True)
        logging.info(f'VideoWriter will write to {self.output_p.resolve()}')
        ims = [Image.fromarray(a_frame) for a_frame in self.frames]
        ims[0].save(self.output_p, save_all=True, append_images=ims[1:], duration=self.duration, disposal=2, loop=0)


class MP4Writer(VideoWriter):
    """ Video writer for creating mp4 videos with cv2.VideoWriter """
    def __init__(self, controller: VideoRenderController) -> None:

        # validate and prep output path
        if isinstance(controller.cfg.output_video_path, NoneType):
            msg = 'output video path not specified for mp4 video writer'
            logging.critical(msg)
            assert False, msg
        output_p = Path(controller.cfg.output_video_path)
        output_p.parent.mkdir(exist_ok=True, parents=True)
        logging.info(f'VideoWriter will write to {output_p.resolve()}')

        # validate and prep codec
        if isinstance(controller.cfg.output_video_codec, NoneType):
            msg = 'output video codec not specified for mp4 video writer'
            logging.critical(msg)
            assert False, msg
        fourcc = cv2.VideoWriter_fourcc(*controller.cfg.output_video_codec)
        logging.info(f'Using codec {controller.cfg.output_video_codec}')

        # calculate video writer framerate
        frame_rate = round(1/controller.delta_t)

        # initialize the video writer
        self.video_writer = cv2.VideoWriter(str(output_p), fourcc, frame_rate, (controller.video_width, controller.video_height))

    def process_frame(self, frame: npt.NDArray[np.uint8]) -> None:
        """ Remove the alpha channel and send to the video writer as it arrives. """
        self.video_writer.write(frame[:, :, :3])

    def cleanup(self) -> None:
        self.video_writer.release()
