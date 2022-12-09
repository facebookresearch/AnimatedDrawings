import numpy as np
from sketch_animate.util import get_show_multi_cameras
from sketch_animate.camera import Camera

from typing import Optional

"""
A class to keep track of all the cameras in a scene and interface with Viewer class to display things on them appropriately.
"""


class CameraManager:

    def __init__(self, viewer):
        self.viewer = viewer
        self.cameras = []
        self.free_camera = None  # only used for observational purposes- can freely move around without changing things
        self.sketch_camera = None  # always focused on sketch, used to calculate the sketch bone angles
        self.bvh_cameras = []
        self.info_cameras = []  # misc. cameras for showing info

    def set_free_camera(self, camera: Camera):
        assert self.free_camera is None, "only one free camera should exist in the scene"
        self.free_camera = camera
        self.cameras.append(camera)

    def set_sketch_camera(self, camera: Camera):
        assert self.sketch_camera is None, "only one sketch camera should exist in the scene"
        self.sketch_camera = camera
        self.cameras.append(camera)

    def add_info_camera(self, camera: Camera):
        self.info_cameras.append(camera)
        self.cameras.append(camera)

    def add_bvh_camera(self, camera: Camera):
        self.bvh_cameras.append(camera)
        self.cameras.append(camera)

    def get_view_matrix(self, camera: Camera):
        return camera.get_view_matrix()

    def get_camera_position(self, camera: Camera):
        return np.array(camera.pos, np.float32)

    def get_proj_matrix(self, win_width, win_height, camera: Camera):
        return camera.get_proj_matrix(win_width, win_height)

    def move_free_camera(self, direction: str):
        self.free_camera.process_keyboard(direction)

    def switch_cameras(self):
        self.cameras.append(self.cameras.pop(0))
        self.free_camera = self.cameras[0]


    def set_sketch_camera_target_position(self, sketch_root_pos: np.ndarray):
        self.sketch_camera.set_target_position(sketch_root_pos)

    def set_bvh_cameras_target_position_and_forward(self, root_pos, root_forward):
        for camera in self.bvh_cameras:
            camera.set_target_position_and_forward(root_pos, root_forward)
