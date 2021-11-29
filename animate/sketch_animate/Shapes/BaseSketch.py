"""Contains sketch classes necessary for generating animations"""
import os
import pickle
import random
from pathlib import Path
from skimage import measure
from numpy import linalg
import OpenGL.GL as GL
import numpy as np
import ctypes
import math
import triangle
from util import normalized, angle_from, rotate, translate, read_texture, scale
from util import get_sketch_segment_visibility
from util import get_sketch_skeleton_visibility
from util import point_in_triangle
from util import get_arap_handles_visibility, get_sketch_mesh_visibility, get_arap_sketch_visibility
from util import bone_colors, colors, squared_distance_between_point_and_line, segment_names, x_ax
from typing import Dict
from collections import deque
import logging

import scipy.sparse as sp
import scipy.sparse.linalg as spla
import scipy.linalg as la

from DataStructures import halfedge

from Shapes.Shapes import Rectangle

from PIL import Image
import cv2

from collections import OrderedDict, defaultdict


class BaseSketch:
    """Contains methods and members common to both Sketch and ARAPSketch classes"""

    class Joint:
        def __init__(self, _joint: Dict, dim: int):
            self.name = _joint['name']

            try:  # dim is tuple with width and height
                loc_x = _joint['loc'][0] / dim[0]
                loc_y = (dim[1] - _joint['loc'][1]) / dim[1]
            except(TypeError):  # dim is int, image is square
                loc_x = _joint['loc'][0] / dim
                loc_y = (dim - _joint['loc'][1]) / dim

            self.loc = np.array([loc_x, loc_y], np.float32)  # location of joint in the sketch

            self.starting_loc = np.array([loc_x, loc_y], np.float32)  # starting location of joint
            self.starting_loc.flags['WRITEABLE'] = False

            self.parent = None

            self.offset = np.array([0.0, 0.0], np.float32)  # xy offset from parent joint
            self.length = 0.0
            self.local_matrix = np.identity(4, np.float32)
            self.global_matrix = np.identity(4, np.float32)

        def set_parent(self, parent):
            self.parent = parent

        def compute_initial_transform(self):
            self.offset = self.loc - self.parent.loc
            self.length = math.sqrt(self.offset[0] ** 2 + self.offset[1] ** 2)

            # skeleton will initially have all bones laid out on y axis and parent rotated. This won't work if a parent has more than one child
            if self.parent.name == 'torso':
                self.local_matrix[0, -1] = self.offset[0]
                self.local_matrix[1, -1] = self.offset[1]



            else:
                self.local_matrix[1, -1] = self.length
                self.global_matrix = self.parent.global_matrix @ self.local_matrix

                desired_orientation = normalized(self.offset)
                current_orientation = normalized(self.global_matrix[0:2, -1] - self.parent.global_matrix[0:2, -1])

                self.parent.starting_theta = angle_from(current_orientation,
                                                        desired_orientation)  # angle between parent bone and this bone orientation in the sketch
                self.parent.starting_global_theta = angle_from(np.array([0, 1], np.float32), normalized(
                    self.offset))  # angle between y axis and this bone in sketch

                rmat = rotate(axis=(0.0, 0.0, 1.0), angle=self.parent.starting_theta)

                self.parent.local_matrix = self.parent.local_matrix @ rmat
                self.parent.update_global_matrix()
                self.update_global_matrix()

        def initialize_matrices(self):
            rmat = rotate(axis=(0.0, 0.0, 1.0), angle=self.starting_theta)
            self.local_matrix = self.local_matrix @ rmat
            self.update_global_matix()

        def update_global_matrix(self):
            if self.name != 'root':
                self.global_matrix = self.parent.global_matrix @ self.local_matrix
            else:
                self.global_matrix = self.local_matrix

        def add_child(self, child):
            self.children.append(child)

    def __init__(self, sketch: Dict):
        self.sketch = sketch
        self.dim = sketch['sketch_dim']  # sketch dimensions. must be square

        self.joints = OrderedDict()
        self.parents = []
        self._initialize_joints(sketch)

        self.render_order = None

        self.model = np.identity(4, np.float32)

        self.segments = OrderedDict()
        self._initialize_segments(sketch['segments'], sketch['image_loc'])

    def _initialize_segments(self, segments: Dict, image_loc: str):
        self.tex_id = read_texture(image_loc, GL.GL_RGBA)  # initialize texture
        for name in segment_names:
            self.segments[name] = self.Segment(segments[name], self.tex_id, self)


    def _initialize_joints(self, sketch: Dict):
        self._build_hierarchy(sketch)
        self._adjust_torso_rotation()
        self._update_global_matrices()

    def _build_hierarchy(self, sketch: Dict):
        """ Called by _initialize_joints. Parses through sketch dictionary's skeleton, creating a joint for each
        and keeping track of the index of that joints parent in the self.joints list """
        for _joint in sketch['skeleton']:
            joint = self.Joint(_joint, self.dim)
            parent_name = _joint['parent']
            if parent_name is None:
                self.parents.append(-1)
            else:
                p_idx = list(self.joints.keys()).index(parent_name)
                self.parents.append(p_idx)
                parent = self.joints[parent_name]
                joint.set_parent(parent)
                joint.compute_initial_transform()
            self.joints[joint.name] = joint

    def _update_global_matrices(self):
        for name, joint in list(self.joints.items()):
            joint.update_global_matrix()


