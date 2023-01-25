# Copyright (c) Meta Platforms, Inc. and affiliates.

from __future__ import annotations
from abc import abstractmethod
from animated_drawings.controller.controller import Controller
from animated_drawings.model.scene import Scene
from animated_drawings.model.animated_drawing import AnimatedDrawing
from animated_drawings.view.view import View
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
        self.video_width, self.video_height = self.view.get_framebuffer_size()

        self.video_writer: VideoWriter = VideoWriter.create_video_writer(self)

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
            if not isinstance(child, AnimatedDrawing):
                continue
            max_frames = max(max_frames, child.retargeter.bvh.frame_max_num)
            frame_time.append(child.retargeter.bvh.frame_time)

        if not all(x == frame_time[0] for x in frame_time):
            msg = f'frame time of BVH files don\'t match. Using first value: {frame_time[0]}'
            logging.warning(msg)

        return max_frames, frame_time[0]

    def _is_run_over(self):
        return self.frames_left_to_render == 0

    def _start_run_loop_iteration(self):
        self.view.clear_window()

    def _tick(self):
        self.scene.progress_time(self.delta_t)

    def _update(self):
        self.scene.update_transforms()

    def _render(self):
        # render the scene
        self.view.render(self.scene)

        # get pixel values from the frame buffer, send them to the video writer
        GL.glBindFramebuffer(GL.GL_READ_FRAMEBUFFER, 0)
        GL.glReadPixels(0, 0, self.video_width, self.video_height, GL.GL_BGRA, GL.GL_UNSIGNED_BYTE, self.frame_data)
        self.video_writer.process_frame(self.frame_data[::-1, :, :].copy())

        # update our counts
        self.frames_left_to_render -= 1
        self.frames_rendered += 1

    def _prep_for_run_loop(self):
        self.start_time = time.time()

    def _cleanup_after_run_loop(self):
        logging.info(f'Rendered {self.frames_rendered} frames in {time.time()-self.start_time} seconds.')

        self.view.cleanup()

        _time = time.time()
        self.video_writer.cleanup()
        logging.info(f'Wrote video to file in in {time.time()-_time} seconds.')


class VideoWriter():
    """ Wrapper to abstract the different backends necessary for writing different video filetypes """

    def __init__(self):
        pass

    @abstractmethod
    def process_frame(self, frame: np.ndarray):
        """ Subclass must specify how to handle each frame of data received. """
        pass

    @abstractmethod
    def cleanup(self):
        """ Subclass must specify how to finish up after all frames have been received. """
        pass

    @staticmethod
    def create_video_writer(controller: VideoRenderController) -> VideoWriter:
        output_p = Path(controller.cfg['OUTPUT_VIDEO_PATH'])
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

    def __init__(self, controller: VideoRenderController):
        self.output_p = Path(controller.cfg['OUTPUT_VIDEO_PATH'])

        self.duration = int(controller.delta_t*1000)
        if self.duration < 20:
            msg = f'Specified FPS of .gif is too high, replacing with 20: {self.duration}'
            logging.warn(msg)
            self.duration = 20

        self.frames = []

    def process_frame(self, frame: np.ndarray):
        """ Reorder channels and save frames as they arrive"""
        self.frames.append(cv2.cvtColor(frame, cv2.COLOR_BGRA2RGBA))

    def cleanup(self):
        """ Write all frames to output path specified."""
        from PIL import Image
        self.output_p.parent.mkdir(exist_ok=True, parents=True)
        logging.info(f'VideoWriter will write to {self.output_p.resolve()}')
        ims = [Image.fromarray(a_frame) for a_frame in self.frames]
        ims[0].save(self.output_p, save_all=True, append_images=ims[1:], duration=self.duration, disposal=2, loop=0)


class MP4Writer(VideoWriter):
    """ Video writer for creating mp4 videos with cv2.VideoWriter """

    def __init__(self, controller: VideoRenderController):
        output_p = Path(controller.cfg['OUTPUT_VIDEO_PATH'])
        output_p.parent.mkdir(exist_ok=True, parents=True)
        logging.info(f'VideoWriter will write to {output_p.resolve()}')

        fourcc = cv2.VideoWriter_fourcc(*controller.cfg['OUTPUT_VIDEO_CODEC'])
        logging.info(f'Using codec {controller.cfg["OUTPUT_VIDEO_CODEC"]}')

        frame_rate = round(1/controller.delta_t)

        self.video_writer = cv2.VideoWriter(str(output_p), fourcc, frame_rate, (controller.video_width, controller.video_height))

    def process_frame(self, frame: np.ndarray):
        """ Remove the alpha channel and send to the video writer as it arrives. """
        self.video_writer.write(frame[:, :, :3])

    def cleanup(self):
        self.video_writer.release()
