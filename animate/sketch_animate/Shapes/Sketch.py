"""Contains sketch classes necessary for generating animations"""
import os
import pickle
from pathlib import Path
from skimage import measure
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

import scipy.sparse as sp
import scipy.sparse.linalg as spla
import scipy.linalg as la

from DataStructures import halfedge

from Shapes.Shapes import Rectangle

from PIL import Image

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


class Sketch(BaseSketch):
    """Class used for Paper Doll style animations. Uses segmentation data and joint transforms to animate"""

    class Segment:

        def __init__(self, segment: Dict, tex_id: int, skeleton):
            self.name = segment['name']
            self.tid0 = tex_id  # texture
            self.clockwise = segment['clockwise']
            self.sketch_dims = skeleton.dim

            self.dist_joint = skeleton.joints[segment['dist_joint']]
            self.prox_joint = skeleton.joints[segment['prox_joint']]

            self.model = rotate([0.0, 0.0, 1.0], -self.prox_joint.starting_global_theta) @ \
                         translate(-self.prox_joint.loc[0], - self.prox_joint.loc[1], 0)

            self.img_coords = segment['img_coords']
            self.points = None
            self.prepare_points_from_img_coords()

            self.vao = GL.glGenVertexArrays(1)
            self.vbo = GL.glGenBuffers(1)
            self.ebo = GL.glGenBuffers(1)

            GL.glBindVertexArray(self.vao)

            # buffer vertex data
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
            GL.glBufferData(GL.GL_ARRAY_BUFFER, self.points, GL.GL_STATIC_DRAW)

            ## buffer element index data
            # GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
            # GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.indices, GL.GL_STATIC_DRAW)

            # position attributes
            GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 4 * self.points.shape[1], None)
            GL.glEnableVertexAttribArray(0)

            # texture attributes
            GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, False, 4 * self.points.shape[1], ctypes.c_void_p(4 * 6))
            GL.glEnableVertexAttribArray(1)

            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
            GL.glBindVertexArray(0)

        def prepare_points_from_img_coords(self):
            vertices = np.array(self.img_coords)

            seg = []
            n = len(self.img_coords)
            for idx in range(n):  # the boundaries of the sketch
                seg.append((idx, (idx + 1) % n))

            a = dict(vertices=vertices, segments=seg, holes=[[-1, -1]])
            b = triangle.triangulate(a, 'qp10')

            self.points = np.empty([3 * len(b['triangles']), 8], np.float32)
            for idx, tri in enumerate(b['triangles']):
                for jdx, vert_idx in enumerate(reversed(tri)):  # reversed so it faces camera
                    vert = b['vertices'][vert_idx]

                    try:  # sketch is rectangle, sketch dim is tuple
                        x = vert[0] / self.sketch_dims[0]
                        y = (self.sketch_dims[1] - vert[1]) / self.sketch_dims[1]
                    except TypeError:  # sketch is square, sketch dim is int or float
                        x = vert[0] / self.sketch_dims
                        y = (self.sketch_dims - vert[1]) / self.sketch_dims

                    self.points[3 * idx + jdx] = x, y, 0, 0, 0, 0, x, y  # pos x3, color x3, texture x2

        def draw(self, **kwargs):
            # assign both textures to their respective texture units
            GL.glBindVertexArray(self.vao)

            GL.glActiveTexture(GL.GL_TEXTURE0)
            GL.glBindTexture(GL.GL_TEXTURE_2D, self.tid0)

            GL.glUseProgram(kwargs['shader_ids']['texture_shader'])
            model_loc = GL.glGetUniformLocation(kwargs['shader_ids']['texture_shader'], "model")
            GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE, self.model.T @ self.prox_joint.global_matrix.T)
            GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.points.shape[0])

            GL.glBindVertexArray(0)

    def __init__(self, sketch: Dict):

        self.tex_id = None

        root = self.joints['root']
        root.local_matrix = translate(root.loc[0], root.loc[1], 0) @ root.local_matrix
        self._update_global_matrices()

        self.vao = GL.glGenVertexArrays(1)
        self.vbo = GL.glGenBuffers(1)
        self.ebo = GL.glGenBuffers(1)

        GL.glBindVertexArray(self.vao)

        self.indices = []
        self._compute_and_buffer_skeleton_element_indices()

        self.points = np.zeros([len(sketch['skeleton']), 6], np.float32)
        self._compute_and_buffer_vertices()

        self._set_attributes()

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def _recompute_points_for_use_without_element_array(self):
        _points = np.empty([self.indices.shape[0], self.points.shape[1]], np.float32)
        for idx, element in enumerate(self.indices):
            _points[idx] = self.points[element]
        self.points = _points
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.points, GL.GL_STATIC_DRAW)

    def _set_attributes(self):
        # position attributes
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 4 * self.points.shape[1], None)
        GL.glEnableVertexAttribArray(0)

        # color attributes
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, False, 4 * self.points.shape[1], ctypes.c_void_p(4 * 3))
        GL.glEnableVertexAttribArray(1)

    def _compute_and_buffer_vertices(self):
        for idx, (name, joint) in enumerate(list(self.joints.items())):
            self.points[idx, 0] = joint.global_matrix[0, -1]  # x position
            self.points[idx, 1] = joint.global_matrix[1, -1]  # y position
            self.points[idx, 2] = 0.0  # z positions
            self.points[idx, 3] = 1.0  # make the lines red
        self._recompute_points_for_use_without_element_array()  # necessary for development on macbook pro

    def _adjust_torso_rotation(self):
        """
        by default, the torso->neck bone should be along the +Yaxis.
        Update the torso rotation and its child offsets to reflect this
        """
        torso = self.joints['torso']
        neck = self.joints['neck']
        rs = self.joints['right_shoulder']
        ls = self.joints['left_shoulder']
        rh = self.joints['right_hip']
        lh = self.joints['left_hip']

        neck_offset = normalized(neck.loc - torso.loc)
        y_axis = np.array([0.0, 1.0], np.float32)
        neck_orientation = angle_from(y_axis, neck_offset)
        torso.starting_global_theta = 0.0
        torso.starting_global_theta = neck_orientation
        torso.local_matrix = rotate([0.0, 0.0, 1.0], -torso.starting_global_theta)
        self._update_global_matrices()

        torso_g_pos = torso.global_matrix[0:2, -1]

        rs_g_pos = rs.global_matrix[0:2, -1]
        rs_l_pos = rs_g_pos - torso_g_pos
        rs.local_matrix[0:2, -1] = rs_l_pos
        rs.local_matrix = rs.local_matrix @ rotate([0.0, 0.0, 1.0], -torso.starting_global_theta)

        ls_g_pos = ls.global_matrix[0:2, -1]
        ls_l_pos = ls_g_pos - torso_g_pos
        ls.local_matrix[0:2, -1] = ls_l_pos
        ls.local_matrix = ls.local_matrix @ rotate([0.0, 0.0, 1.0], -torso.starting_global_theta)

        rh_g_pos = rh.global_matrix[0:2, -1]
        rh_l_pos = rh_g_pos - torso_g_pos
        rh.local_matrix[0:2, -1] = rh_l_pos
        rh.local_matrix = rh.local_matrix @ rotate([0.0, 0.0, 1.0], -torso.starting_global_theta)

        lh_g_pos = lh.global_matrix[0:2, -1]
        lh_l_pos = lh_g_pos - torso_g_pos
        lh.local_matrix[0:2, -1] = lh_l_pos
        lh.local_matrix = lh.local_matrix @ rotate([0.0, 0.0, 1.0], -torso.starting_global_theta)

        n_g_pos = neck.global_matrix[0:2, -1]
        n_l_pos = n_g_pos - torso_g_pos
        neck.local_matrix[0:2, -1] = n_l_pos
        neck.local_matrix = neck.local_matrix @ rotate([0.0, 0.0, 1.0], -torso.starting_global_theta)

        torso.local_matrix = rotate([0.0, 0.0, 1.0], torso.starting_global_theta)

    def _update_global_matrices(self):
        for name, joint in list(self.joints.items()):
            joint.update_global_matrix()

    def _compute_and_buffer_skeleton_element_indices(self):
        for c_id, p_id in enumerate(self.parents):  # child id, parent id
            if p_id == -1:
                continue
            self.indices.append(c_id)
            self.indices.append(p_id)
        self.indices = np.array(self.indices, np.uint)
        # buffer element index data
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.indices, GL.GL_STATIC_DRAW)

    def set_render_order(self, proj_cam, bvh, time):
        distances = []
        for key, segment in self.segments.items():
            pj_name = segment.prox_joint.name
            bvh_jnt_name = bvh.jnt_map[pj_name]
            idx = bvh.joint_names.index(bvh_jnt_name)
            pj_pos = bvh.pos[time, idx, :]
            pj_pos = np.array([*pj_pos, 1.0], np.float32)
            pj_pos = bvh.model @ pj_pos

            cam_pos = proj_cam.get_global_position()
            distance = np.linalg.norm(pj_pos[[0, 2]] - cam_pos[[0, 2]])
            distances.append((segment, distance))

        self.render_order = sorted(distances, key=lambda item: item[1], reverse=True)  # used in segments

    def _draw_segments(self, **kwargs):
        if self.render_order is not None:
            for segment, _ in self.render_order:
                segment.draw(**kwargs)
        else:
            for key, segment in self.segments.items():
                segment.draw(**kwargs)

    def _draw_skeleton(self, **kwargs):
        self._update_global_matrices()
        self._compute_and_buffer_vertices()

        GL.glUseProgram(kwargs['shader_ids']['color_shader'])
        model_loc = GL.glGetUniformLocation(kwargs['shader_ids']['color_shader'], "model")
        GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE, self.model)

        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_LINES, 0, len(self.joints) * 2)

    def draw(self, **kwargs):
        if kwargs['camera'].name == 'projection_view':
            return

        if get_sketch_segment_visibility():
            self._draw_segments(**kwargs)

        if get_sketch_skeleton_visibility():
            self._draw_skeleton(**kwargs)


class ARAP_Sketch(BaseSketch):
    """As-rigid-as-possible animations. Uses joint positions as handles for ARAP"""

    class Segment:

        def __init__(self, segment: Dict, tex_id: int, skeleton):
            self.name = segment['name']
            self.tid0 = tex_id
            self.clockwise = segment['clockwise']
            self.sketch_dims = skeleton.dim

            self.dist_joint = skeleton.joints[segment['dist_joint']]
            self.prox_joint = skeleton.joints[segment['prox_joint']]

            self.starting_theta = angle_from(x_ax, normalized(self.dist_joint.starting_loc - self.prox_joint.starting_loc))

            self.model = rotate([0.0, 0.0, 1.0], -self.prox_joint.starting_global_theta) @ \
                         translate(-self.prox_joint.loc[0], - self.prox_joint.loc[1], 0)

            self.img_coords = segment['img_coords']
            self.points = None
            self.prepare_points_from_img_coords()

            self.vao = GL.glGenVertexArrays(1)
            self.vbo = GL.glGenBuffers(1)

            GL.glBindVertexArray(self.vao)

            # buffer vertex data
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
            GL.glBufferData(GL.GL_ARRAY_BUFFER, self.points, GL.GL_STATIC_DRAW)

            # position attributes
            GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 4 * self.points.shape[1], None)
            GL.glEnableVertexAttribArray(0)

            # color attributes
            GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, False, 4 * self.points.shape[1], ctypes.c_void_p(4 * 3))
            GL.glEnableVertexAttribArray(1)

            # texture attributes
            GL.glVertexAttribPointer(2, 2, GL.GL_FLOAT, False, 4 * self.points.shape[1], ctypes.c_void_p(4 * 6))
            GL.glEnableVertexAttribArray(2)

            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
            GL.glBindVertexArray(0)

        def prepare_points_from_img_coords(self):
            vertices = np.array(self.img_coords)

            seg = []
            n = len(self.img_coords)
            for idx in range(n):  # the boundaries of the sketch
                seg.append((idx, (idx + 1) % n))

            a = dict(vertices=vertices, segments=seg, holes=[[-1, -1]])
            b = triangle.triangulate(a, 'qp10')

            self.points = np.empty([3 * len(b['triangles']), 8], np.float32)
            for idx, tri in enumerate(b['triangles']):
                for jdx, vert_idx in enumerate(reversed(tri)):  # reversed so it faces camera
                    vert = b['vertices'][vert_idx]

                    try:  # sketch is rectangle, sketch dim is tuple
                        x = vert[0] / self.sketch_dims[0]
                        y = (self.sketch_dims[1] - vert[1]) / self.sketch_dims[1]
                    except TypeError:  # sketch is square, sketch dim is int or float
                        x = vert[0] / self.sketch_dims
                        y = (self.sketch_dims - vert[1]) / self.sketch_dims

                    self.points[3 * idx + jdx] = x, y, 0, 0, 0, 0, x, y  # pos x3, color x3, texture x2

        def draw(self, **kwargs):
            # assign both textures to their respective texture units
            GL.glBindVertexArray(self.vao)

            GL.glActiveTexture(GL.GL_TEXTURE0)
            GL.glBindTexture(GL.GL_TEXTURE_2D, self.tid0)

            GL.glUseProgram(kwargs['shader_ids']['texture_shader'])
            model_loc = GL.glGetUniformLocation(kwargs['shader_ids']['texture_shader'], "model")
            GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE, self.model.T @ self.prox_joint.global_matrix.T)
            GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.points.shape[0])

            # GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
            # GL.glUseProgram(kwargs['shader_ids']['color_shader'])
            # model_loc = GL.glGetUniformLocation(kwargs['shader_ids']['color_shader'], "model")
            # GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE, self.model.T @ self.prox_joint.global_matrix.T)
            # GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.points.shape[0])
            # GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)

            GL.glBindVertexArray(0)

    class ARAP_Handle:

        def __init__(self, pjoint, joint, v_idx=None, bary_coords=None, dim=None, arap_sketch=None):

            # if djoint.name == 'torso':
            #     color = (255, 0, 0)
            # else:
            #     color = 'blue'
            color = (255, 0, 0)
            self.widget = Rectangle(color=color)
            self.dim = dim
            self.pjoint = pjoint  # the parent joint of this joint
            self.joint = joint  # joint the handle corresponds to

            self.arap_sketch = arap_sketch  # needed so we can apply it's model transform to handles for viewing

            self.cx, self.cy = None, None
            self.set_world_coords()
            # self.cx, self.cy = v[0], v[1]

            self.widget.set_position(self.cx, self.cy, 0)
            self.widget.set_uniform_scale(0.01)

            if bary_coords is None:
                assert v_idx is not None
                self.v_idx = [[v_idx, 1.0]]  # [[vertex_idx, weight]]
            else:
                self.v_idx = [
                    [bary_coords[0][0], bary_coords[0][1]],
                    [bary_coords[1][0], bary_coords[1][1]],
                    [bary_coords[2][0], bary_coords[2][1]]
                ]

        def set_world_coords(self):

            self.cx, self.cy = self.joint.global_matrix[0:2, -1][0:2]

            self.widget.set_position(self.cx + self.arap_sketch.model[0, -1], self.cy + self.arap_sketch.model[1, -1],
                                     0)

        def set_handle(self, x, y):
            assert x is not None
            assert y is not None
            self.cx = x
            self.cy = y
            self.widget.set_position(self.cx, self.cy, 0)

        # def move_handle(self, x=None, y=None):
        #     if x:
        #         self.cx += x
        #     if y:
        #         self.cy += y
        #     # self.widget.set_position(self.cx / self.dim, (self.dim - self.cy) / self.dim, 0)
        #     self.widget.set_position(self.cx, self.cy, 0)

        def draw(self, **kwargs):
            self.widget.draw(**kwargs)

    class Bone:
        """
        A bone connects a pair of ARAP_Handle points (joints).
        Mesh vertices will be attached to specific bones for skinning purpose.
        """

        def __init__(self, arap_handle, idx,
                     arap_sketch):  # because each arap_handle is based on a joint, and has it's parent joint as a member, we can make bone from it

            self.arap_handle = arap_handle

            self.arap_sketch = arap_sketch  # arap_sketch this bone belongs to. needed to access it's mesh vertices

            self.idx = idx  # useful for coloring

            self.assigned_vertices = []  # vertices that are assigned to this bone for skinning purposes

            self.vao = GL.glGenVertexArrays(1)
            self.vbo = GL.glGenBuffers(1)

            self.djoint = self.arap_handle.joint
            self.pjoint = self.arap_handle.pjoint

            self.points = np.zeros([2, 6], dtype=np.float32)
            self.points[:, 3:] = colors[idx]
            self.dj_loc = None
            self.pj_loc = None
            self.update_position()

            GL.glBindVertexArray(self.vao)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
            GL.glBufferData(GL.GL_ARRAY_BUFFER, self.points, GL.GL_DYNAMIC_DRAW)

            # position attributes
            GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 4 * self.points.shape[1], None)
            GL.glEnableVertexAttribArray(0)

            # color attributes
            GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, False, 4 * self.points.shape[1], ctypes.c_void_p(4 * 3))
            GL.glEnableVertexAttribArray(1)

            GL.glBindVertexArray(0)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

        def _prep_vertex_connectors(self):
            # from https://diego.assencio.com/?index=ec3d5dfdfc0b6a0d147a656f0af332bd
            self.vert_assign_points = np.zeros([len(self.assigned_vertices) * 2, 6], dtype=np.float32)
            self.vert_assign_lambas = np.zeros([len(self.assigned_vertices)], dtype=np.float32)

            for idx, vertex_idx in enumerate(self.assigned_vertices):
                p = np.array(self.dj_loc)
                q = np.array(self.pj_loc)
                x = np.array(self.arap_sketch.mesh_vertices[vertex_idx, 0:2])
                lambda_s = np.dot(x - p, q - p) / np.dot(q - p, q - p)
                if lambda_s < 0:
                    s = p
                elif lambda_s > 1:
                    s = q
                else:
                    s = p + lambda_s * (q - p)
                self.vert_assign_points[2 * idx, 0:2] = x
                self.vert_assign_points[2 * idx + 1, 0:2] = s

                self.vert_assign_points[2 * idx, 3:] = colors[self.idx]
                self.vert_assign_points[2 * idx + 1, 3:] = colors[self.idx]

                self.vert_assign_lambas[idx] = lambda_s

            self.vc_vao = GL.glGenVertexArrays(1)  # vertex connector vao
            self.vc_vbo = GL.glGenBuffers(1)  # vertex connector vbo
            GL.glBindVertexArray(self.vc_vao)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vc_vbo)
            GL.glBufferData(GL.GL_ARRAY_BUFFER, self.vert_assign_points, GL.GL_DYNAMIC_DRAW)

            # position attributes
            GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 4 * self.vert_assign_points.shape[1], None)
            GL.glEnableVertexAttribArray(0)

            # color attributes
            GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, False, 4 * self.vert_assign_points.shape[1],
                                     ctypes.c_void_p(4 * 3))
            GL.glEnableVertexAttribArray(1)

            GL.glBindVertexArray(0)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

        def update_position(self):
            self.dj_loc = self.arap_handle.joint.global_matrix[0:2, -1][0:2]
            self.pj_loc = self.arap_handle.pjoint.global_matrix[0:2, -1][0:2]

            self.points[0, 0:2] = self.dj_loc
            self.points[1, 0:2] = self.pj_loc

            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
            GL.glBufferData(GL.GL_ARRAY_BUFFER, self.points, GL.GL_DYNAMIC_DRAW)

        def draw(self, **kwargs):
            GL.glUseProgram(kwargs['shader_ids']['color_shader'])

            GL.glBindVertexArray(self.vao)
            GL.glDrawArrays(GL.GL_LINES, 0, 2)
            GL.glBindVertexArray(0)


    def __init__(self, sketch: Dict, cfg):
        self.cfg = cfg
        super(ARAP_Sketch, self).__init__(sketch)

        self.model = None  # this is the root transform of the character
        self._initialize_model()

        self.mask = None  # PIL.Image binary mask of the character
        self.triangle_mesh = None  # dictionary with mesh generated by Triangle from self.mask
        self._generate_mesh()

        self.arap_handles = []
        self._get_joint_constraints()

        self.bones = []
        self._initialize_bones()

        self.tri2bone = {}
        self._assign_triangles_to_bones()

        self.indices = None
        self.indices_info = None
        self._prepare_indices()

        self.mesh_vertices = None
        self._buffer_vertices()

        self._arap_setup()
        self._arap_solve()

        self._image_loc = sketch['image_loc']

        self.tex_id = None
        self.vao = None
        self.vbo = None
        self.ebo = None

        with open(os.path.join(Path(sketch['image_loc']).parent, 'ARAP_Sketch.pickle'), 'wb') as f:
            pickle.dump(self, f)

        self._initialize_opengl()

    @staticmethod
    def load_from_pickle(pickle_fn):
        with open(pickle_fn, 'rb') as f:
            ret = pickle.load(f)
        ret._initialize_opengl()
        return ret

    def _initialize_opengl(self):

        self.tex_id = read_texture(self._image_loc, GL.GL_RGBA)  # initialize texture and store texture id

        self.vao = GL.glGenVertexArrays(1)
        self.vbo = GL.glGenBuffers(1)
        self.ebo = GL.glGenBuffers(1)

        GL.glBindVertexArray(self.vao)

        # buffer vertex data
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.mesh_vertices, GL.GL_DYNAMIC_DRAW)

        # buffer element index data
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.indices, GL.GL_STATIC_DRAW)

        # position attributes
        GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, False, 4 * self.mesh_vertices.shape[1], None)
        GL.glEnableVertexAttribArray(0)

        # texture attributes
        GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, False, 4 * self.mesh_vertices.shape[1], ctypes.c_void_p(4 * 3))
        GL.glEnableVertexAttribArray(1)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def _initialize_model(self):
        """ Creates character's root transform. Is identity matrix, with translational offset based on where
        the character's root joint within the image is. Called only once, during __init__"""

        self.model = np.identity(4, np.float32)

        # Below is useful only if we want to position the character somewhere other than origin
        # root_loc = self.sketch['skeleton'][0]['loc']
        # root_offset_img_x = root_loc[0] / self.sketch['sketch_dim']
        # root_offset_img_y = root_loc[1] / self.sketch['sketch_dim']

        # root_offset_world_x = -0.5 + root_offset_img_x
        # root_offset_world_y = 0.5 - root_offset_img_y

        # self.model[0, -1] = root_offset_world_x
        # self.model[1, -1] = root_offset_world_y

        # self.model[0, -1] = 0
        # self.model[1, -1] = 0


    def _adjust_torso_rotation(self):
        """
        by default, the torso->neck bone should be along the +Yaxis.
        Update the torso rotation and its child offsets to reflect this
        """
        torso = self.joints['torso']
        neck = self.joints['neck']
        rs = self.joints['right_shoulder']
        ls = self.joints['left_shoulder']
        rh = self.joints['right_hip']
        lh = self.joints['left_hip']

        if self.cfg['SHOW_ORIGINAL_POSE_ONLY']:
            torso.starting_global_theta = 0.0
            print('test')
            return

        neck_offset = normalized(neck.loc - torso.loc)
        y_axis = np.array([0.0, 1.0], np.float32)
        neck_orientation = angle_from(y_axis, neck_offset)
        torso.starting_global_theta = 0.0
        torso.starting_global_theta = neck_orientation
        torso.local_matrix = rotate([0.0, 0.0, 1.0], -torso.starting_global_theta)
        self._update_global_matrices()

        torso_g_pos = torso.global_matrix[0:2, -1]

        rs_g_pos = rs.global_matrix[0:2, -1]
        rs_l_pos = rs_g_pos - torso_g_pos
        rs.local_matrix[0:2, -1] = rs_l_pos
        rs.local_matrix = rs.local_matrix @ rotate([0.0, 0.0, 1.0], -torso.starting_global_theta)

        ls_g_pos = ls.global_matrix[0:2, -1]
        ls_l_pos = ls_g_pos - torso_g_pos
        ls.local_matrix[0:2, -1] = ls_l_pos
        ls.local_matrix = ls.local_matrix @ rotate([0.0, 0.0, 1.0], -torso.starting_global_theta)

        rh_g_pos = rh.global_matrix[0:2, -1]
        rh_l_pos = rh_g_pos - torso_g_pos
        rh.local_matrix[0:2, -1] = rh_l_pos
        rh.local_matrix = rh.local_matrix @ rotate([0.0, 0.0, 1.0], -torso.starting_global_theta)

        lh_g_pos = lh.global_matrix[0:2, -1]
        lh_l_pos = lh_g_pos - torso_g_pos
        lh.local_matrix[0:2, -1] = lh_l_pos
        lh.local_matrix = lh.local_matrix @ rotate([0.0, 0.0, 1.0], -torso.starting_global_theta)

        n_g_pos = neck.global_matrix[0:2, -1]
        n_l_pos = n_g_pos - torso_g_pos
        neck.local_matrix[0:2, -1] = n_l_pos
        neck.local_matrix = neck.local_matrix @ rotate([0.0, 0.0, 1.0], -torso.starting_global_theta)

        torso.local_matrix = rotate([0.0, 0.0, 1.0], torso.starting_global_theta)

    def _initialize_bones(self):
        for idx, handle in enumerate(self.arap_handles):
            self.bones.append(self.Bone(handle, idx, self))

    def set_render_order(self, proj_cam, bvh, time):
        """ For each bone in the BVH, get it's midpoint and find the distance to the camera, sort be increasing"""
        cam_pos = proj_cam.get_global_position()

        distances = {
            'right_arm': [],
            'left_arm': [],
            'right_leg': [],
            'left_leg': [],
            'torso': []
        }

        for b_idx, bone in enumerate(self.bones):
            # distal joint
            d_bvh_jnt_name = bvh.jnt_map[bone.djoint.name]
            d_idx = bvh.joint_names.index(d_bvh_jnt_name)
            d_joint_pos = bvh.pos[time, d_idx, :]
            d_joint_pos = np.array([*d_joint_pos, 1.0], np.float32)
            d_joint_pos = bvh.model @ d_joint_pos

            # proximal joint
            p_bvh_jnt_name = bvh.jnt_map[bone.pjoint.name]
            p_idx = bvh.joint_names.index(p_bvh_jnt_name)
            p_joint_pos = bvh.pos[time, p_idx, :]
            p_joint_pos = np.array([*p_joint_pos, 1.0], np.float32)
            p_joint_pos = bvh.model @ p_joint_pos

            bone_mid_pos = (p_joint_pos + d_joint_pos) / 2 # midpoint

            distance = np.linalg.norm(bone_mid_pos[[0, 2]] - cam_pos[[0, 2]])

            if bone.djoint.name in ['right_elbow', 'right_hand']:
                distances['right_arm'].append([b_idx, distance, bone.djoint.name])
            elif bone.djoint.name in ['left_elbow', 'left_hand']:
                distances['left_arm'].append([b_idx, distance, bone.djoint.name])
            elif bone.djoint.name in ['right_knee', 'right_foot']:
                distances['right_leg'].append([b_idx, distance, bone.djoint.name])
            elif bone.djoint.name in ['left_knee', 'left_foot']:
                distances['left_leg'].append([b_idx, distance, bone.djoint.name])
            else:
                distances['torso'].append([b_idx, distance, bone.djoint.name])

        for key, val in distances.items():
            distances[key] = sorted(val, key=lambda item: item[1], reverse=True)  # used in segments

        render_order = []
        while distances:
            max_, max_key = -np.inf, list(distances.keys())[0]
            for key, val in distances.items():
                if val and val[0][1] > max_:
                    max_, max_key = val[0][1], key
            render_order += distances[max_key]
            del(distances[max_key])
        self.render_order = render_order


    def draw(self, **kwargs):

        self._update_global_matrices()
        for arap_handle in self.arap_handles:
            arap_handle.set_world_coords()
        self._arap_solve()

        for bone in self.bones:
            bone.update_position()

        GL.glBindVertexArray(self.vao)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)  # buffer vertex data
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.mesh_vertices, GL.GL_DYNAMIC_DRAW)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        GL.glBindVertexArray(self.vao)

        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.tex_id)

        # render the sketch texture
        if get_arap_sketch_visibility() and kwargs['camera'].cam_type not in ['triangulation']:
            GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
            GL.glUseProgram(kwargs['shader_ids']['texture_shader'])
            model_loc = GL.glGetUniformLocation(kwargs['shader_ids']['texture_shader'], "model")
            GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE, self.model.T)

            if self.render_order is not None:
                for bone_idx, _, _ in self.render_order:
                    if bone_idx not in self.indices_info.keys():
                        continue
                    start, length = self.indices_info[bone_idx]
                    GL.glDrawElements(GL.GL_TRIANGLES, length, GL.GL_UNSIGNED_INT, ctypes.c_void_p(4 * start))
            else:
                GL.glDrawElements(GL.GL_TRIANGLES, self.indices.shape[0], GL.GL_UNSIGNED_INT, None)

        # render the mesh
        if self.cfg['SHOW_SKETCH_MESH'] or kwargs['camera'].cam_type in ['triangulation']:
            GL.glUseProgram(kwargs['shader_ids']['bone_assignment'])
            model_loc = GL.glGetUniformLocation(kwargs['shader_ids']['bone_assignment'], "model")
            GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE, self.model.T)
            color_loc = GL.glGetUniformLocation(kwargs['shader_ids']['bone_assignment'], "in_color")
            color_black_loc = GL.glGetUniformLocation(kwargs['shader_ids']['color_shader'], "color_black")

            if self.render_order is not None:
                for bone_idx, _, _ in self.render_order:
                    if bone_idx not in self.indices_info.keys():
                        continue
                    start, length = self.indices_info[bone_idx]

                    # draw mesh color, which indicates closest bone
                    if self.cfg['DRAW_SKETCH_BONE_COLORS']:
                        GL.glUniform3f(color_loc, *np.array(bone_colors[bone_idx], dtype=np.float32).tolist())
                        GL.glDrawElements(GL.GL_TRIANGLES, length, GL.GL_UNSIGNED_INT, ctypes.c_void_p(4 * start))

                    # draw mesh edges
                    GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
                    GL.glUniform1i(color_black_loc, GL.GL_TRUE)
                    GL.glDrawElements(GL.GL_TRIANGLES, length, GL.GL_UNSIGNED_INT, ctypes.c_void_p(4 * start))
                    GL.glUniform1i(color_black_loc, GL.GL_FALSE)
                    GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)

        GL.glBindVertexArray(0)

        if get_arap_handles_visibility() or kwargs['camera'].cam_type in ['triangulation']:
            for c in self.arap_handles:
                c.draw(**kwargs)

        if get_sketch_segment_visibility():
            GL.glUseProgram(kwargs['shader_ids']['color_shader'])
            model_loc = GL.glGetUniformLocation(kwargs['shader_ids']['color_shader'], "model")
            GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE, self.model.T)
            for b in self.bones:
                b.draw(**kwargs)

    def _prepare_indices(self):
        """
        Prepares index element array self.indices
        Also prepares self.indices_info, which keeps track of how many vertices belong to triangles belonging to each joint and where they start
        """
        _bone2verts = defaultdict(list)
        for triangle_idx, bone_idx in self.tri2bone.items():
            vertex_ids = self.triangle_mesh['triangles'][triangle_idx]
            _bone2verts[bone_idx].append(vertex_ids)
        for joint_idx in _bone2verts.keys():
            _bone2verts[joint_idx] = np.stack(_bone2verts[joint_idx]).flatten()[::-1]  # reverse so it isn't culled

        self.indices_info = {}
        self.indices = np.empty(0)
        for key in _bone2verts.keys():
            self.indices_info[key] = (self.indices.shape[0], _bone2verts[key].shape[0])  # starting index, length
            self.indices = np.concatenate((self.indices, _bone2verts[key]))
        self.indices = self.indices.astype(np.int32)

    def _generate_mesh(self):
        mask_path = os.path.abspath(self.sketch['image_loc'][:-4] + '_mask.png')
        if not os.path.exists(mask_path):
            assert False, 'Couldn\'t find mask file: {}'.format(mask_path)

        self.mask = Image.open(mask_path)
        mask_ar = np.array(self.mask)[:, :, -1]
        contours = measure.find_contours(mask_ar, 128)
        contour = []

        # if multiple contours found, use the largest
        max_idx, max_len = -1, 0
        for idx, c in enumerate(contours):
            if len(c) > max_len:
                max_len = len(c)
                max_idx = idx
        assert max_idx != -1

        try:  # img is rectangle
            for idx in range(0, len(contours[max_idx]), 15):
                contour.append((contours[max_idx][idx][1] / self.dim[1], contours[max_idx][idx][0] / self.dim[0]))
        except TypeError:  # img is square
            for idx in range(0, len(contours[max_idx]), 15):
                contour.append((contours[max_idx][idx][1] / self.dim, contours[max_idx][idx][0] / self.dim))

        segs = []
        for idx, _ in enumerate(contour):
            segs.append((idx, (idx + 1) % len(contour)))
        a = dict(vertices=contour, segments=segs, holes=[[-1, -1]])
        self.triangle_mesh = triangle.triangulate(a, 'qpa100')

    def _buffer_vertices(self):
        vert_count = self.triangle_mesh['vertices'].shape[0]
        self.mesh_vertices = np.empty((vert_count, 5), np.float32)
        for idx in range(0, vert_count):
            self.mesh_vertices[idx, 0] = self.triangle_mesh['vertices'][idx][0]         # x pos
            self.mesh_vertices[idx, 1] = 1 - self.triangle_mesh['vertices'][idx][1]     # y pos
            self.mesh_vertices[idx, 2] = 0                                              # z pos
            self.mesh_vertices[idx, 3] = self.triangle_mesh['vertices'][idx][0]         # x tex
            self.mesh_vertices[idx, 4] = 1 - self.triangle_mesh['vertices'][idx][1]     # y tex
        return

    def _assign_triangles_to_bones(self):
        """Called during construction to determine which triangles belong to which bone. Used for depth ordering"""

        mask_img = Image.open(self.sketch['image_loc'][:-4] + '_mask.png').convert('1')
        mask_np = np.transpose(np.array(mask_img).astype(np.bool))

        distances = np.empty([len(self.bones), *mask_np.shape], dtype=np.int)
        for idx, bone in enumerate(self.bones):
            joint_img_coord1 = [bone.djoint.loc[0], 1 - bone.djoint.loc[1]]
            x1 = int(joint_img_coord1[0] * mask_np.shape[0])
            y1 = int(joint_img_coord1[1] * mask_np.shape[1])

            joint_img_coord2 = [bone.pjoint.loc[0], 1 - bone.pjoint.loc[1]]
            x2 = int(joint_img_coord2[0] * mask_np.shape[0])
            y2 = int(joint_img_coord2[1] * mask_np.shape[1])

            # BFS variables
            distance = np.zeros(mask_np.shape, dtype=np.int)
            in_queue = np.zeros(mask_np.shape, dtype=np.bool)
            queue = []

            # BFS seed with points along bone
            seeds = []
            for _p in range(0, 100):
                p = _p / 100
                point = int(round(x1 + p * (x2-x1))),  int(round(y1 + p * (y2 - y1)))
                seeds.append(point)
            seeds = list(set(seeds))  # dedups
            for seed in seeds:
                queue.append(seed)
                in_queue[seed] = True

            # BFS search
            while queue:
                x, y = queue.pop(0)
                for _x, _y in [(x - 1, y - 1), (x + 0, y - 1), (x + 1, y - 1),
                               (x - 1, y + 0), (x + 1, y + 0),
                               (x - 1, y + 1), (x + 0, y + 1), (x + 1, y + 1)]:

                    if in_queue[_x, _y] or not mask_np[_x, _y]:
                        continue
                    queue.append((_x, _y))
                    in_queue[_x, _y] = True
                    distance[_x, _y] = distance[x, y] + 1

            distances[idx] = np.transpose(distance)

        self.tri2bone = {}
        # for each triangle, get centroid and use it to find closest bone
        for idx, t in enumerate(self.triangle_mesh['triangles']):
            _v0, _v1, _v2 = self.triangle_mesh['vertices'][t[0:3]]
            v0 = [int(_v0[0] * mask_np.shape[0]), int((_v0[1]) * mask_np.shape[1])]
            v1 = [int(_v1[0] * mask_np.shape[0]), int((_v1[1]) * mask_np.shape[1])]
            v2 = [int(_v2[0] * mask_np.shape[0]), int((_v2[1]) * mask_np.shape[1])]
            centroid_x, centroid_y = int((v0[0] + v1[0] + v2[0]) / 3), int((v0[1] + v1[1] + v2[1]) / 3)
            closest_bone_idx = distances[:, centroid_y, centroid_x].argmin()
            self.tri2bone[idx] = closest_bone_idx

    def _get_joint_constraints(self):
        """Called once during object construction to generate the joint-drived ARAP constraints"""

        def get_barycentric_coords(p, a, b, c):
            v0 = b - a
            v1 = c - a
            v2 = p - a
            d00 = np.dot(v0, v0)
            d01 = np.dot(v0, v1)
            d11 = np.dot(v1, v1)
            d20 = np.dot(v2, v0)
            d21 = np.dot(v2, v1)
            denom = d00 * d11 - d01 * d01
            v = (d11 * d20 - d01 * d21) / denom
            w = (d00 * d21 - d01 * d20) / denom
            u = 1.0 - v - w

            return u, v, w

        # get arap constraints that make up the bones
        for name in self.joints.keys():
            if self.joints[name].parent is None or self.joints[name].parent.name == 'root':  # root motion is handled
                continue

            parent_name = self.joints[name].parent.name
            image_coords = [self.joints[name].loc[0], 1 - self.joints[name].loc[1]]

            intermediate_image_coords = image_coords[0], image_coords[1]
            for t in self.triangle_mesh['triangles']:
                v0 = self.triangle_mesh['vertices'][t[0]]
                v1 = self.triangle_mesh['vertices'][t[1]]
                v2 = self.triangle_mesh['vertices'][t[2]]
                if point_in_triangle(intermediate_image_coords, v0, v1, v2):
                    w = get_barycentric_coords(intermediate_image_coords, v0, v1, v2)
                    handle = self.ARAP_Handle(self.joints[name].parent,
                                              self.joints[name],
                                              bary_coords=[[t[0], w[0]], [t[1], w[1]], [t[2], w[2]]],
                                              dim=self.dim,
                                              arap_sketch=self)
                    self.arap_handles.append(handle)
                    break

    #######################
    # Begin ARAP functions.
    #######################
    def _arap_solve(self):

        self.pinPoses = []
        for handle in self.arap_handles:
            self.pinPoses.append((handle.cx, 1 - handle.cy))
        self.pinPoses = np.asarray(self.pinPoses)

        b1 = self._buildB1(self.pinPoses, self.w, self.nEdges)
        v1 = spla.spsolve(self.tA1 * self.A1, self.tA1 * b1)

        b2 = self._buildB2(self.heVectors, self.heIndices, self.edges, self.pinPoses, self.w, self.G, v1)
        v2x = spla.spsolve(self.tA2 * self.A2, self.tA2 * b2[:, 0])
        v2y = spla.spsolve(self.tA2 * self.A2, self.tA2 * b2[:, 1])
        v2 = np.vstack((v2x, v2y)).T

        for idx in range(self.mesh_vertices.shape[0]):
            self.mesh_vertices[idx, 0] = v2[idx][0]
            self.mesh_vertices[idx, 1] = 1 - v2[idx][1]

        # for idx, tri in enumerate(self.triangle_mesh['triangles']):
        #     for jdx, vert_idx in enumerate(reversed(tri)):  # reversed so it faces camera
        #         self.mesh_vertices[3 * idx + jdx, 0] = v2[vert_idx][0]
        #         self.mesh_vertices[3 * idx + jdx, 1] = 1 - v2[vert_idx][1]

    def _arap_setup(self):
        """ Called once during object construction to generate the reusable parts of the ARAP matrices"""
        self.xy = self.triangle_mesh['vertices']
        self.halfedges = halfedge.build(self.triangle_mesh['triangles'])  # builds the halfedge structure from triangles
        self.heVectors = np.asarray([self.xy[he.ivertex, :] - self.xy[he.prev().ivertex, :] for he in self.halfedges])
        self.pins = []
        for handle in self.arap_handles:
            self.pins.append(handle.v_idx)
        self.pins = np.asarray(self.pins)

        self.w = 1000.0
        self.nVertices = self.xy.shape[0]
        self.edges, self.heIndices = halfedge.toEdge(self.halfedges)
        self.nEdges = self.edges.shape[0]
        self.A1top, self.G = self._buildA1top(self.heVectors, self.halfedges, self.edges, self.heIndices,
                                              self.nVertices)

        self.A1bottom = self._buildA1bottom(self.pins, self.w, self.nVertices)

        self.A1 = sp.vstack((self.A1top, self.A1bottom))
        self.tA1 = self.A1.transpose()

        self.A2top = self._buildA2top(self.edges, self.nVertices)
        self.A2bottom = self._buildA2bottom(self.pins, self.w, self.nVertices)
        self.A2 = sp.vstack((self.A2top, self.A2bottom))
        self.tA2 = self.A2.transpose()

    def _buildA1top(self, heVectors, halfedges, edges, heIndices, nVertices):

        threeVertices2twoEdges = np.asarray(((-1., 0., 1., 0., 0., 0.),
                                             (0., -1., 0., 1., 0., 0.),
                                             (-1., 0., 0., 0., 1., 0.),
                                             (0., -1., 0., 0., 0., 1.)))
        fourVertices2threeEdges = np.asarray(((-1., 0., 1., 0., 0., 0., 0., 0.),
                                              (0., -1., 0., 1., 0., 0., 0., 0.),
                                              (-1., 0., 0., 0., 1., 0., 0., 0.),
                                              (0., -1., 0., 0., 0., 1., 0., 0.),
                                              (-1., 0., 0., 0., 0., 0., 1., 0.),
                                              (0., -1., 0., 0., 0., 0., 0., 1.)))

        Arows = []
        Acols = []
        Adata = []
        Grows = []
        Gcols = []
        Gdata = []
        for row in range(0, edges.shape[0]):
            v0, v1 = edges[row, :]
            Arows.append(2 * row);
            Acols.append(2 * v0);
            Adata.append(-1.0)
            Arows.append(2 * row);
            Acols.append(2 * v1);
            Adata.append(1.0)
            Arows.append(2 * row + 1);
            Acols.append(2 * v0 + 1);
            Adata.append(-1.0)
            Arows.append(2 * row + 1);
            Acols.append(2 * v1 + 1);
            Adata.append(1.0)

            vertices = [v0, v1]
            he = halfedges[heIndices[row]]
            edgeVectors = [heVectors[he.iself], ]
            vertices.append(halfedges[he.inext].ivertex)
            edgeVectors.append(-heVectors[he.prev().iself])
            verts2edges = threeVertices2twoEdges
            if he.ipair != -1:
                pair = halfedges[he.ipair]
                vertices.append(halfedges[pair.inext].ivertex)
                edgeVectors.append(heVectors[pair.inext])
                verts2edges = fourVertices2threeEdges
            g = []
            for v in edgeVectors:
                g.extend(((v[0], v[1]), (v[1], -v[0])))
            g = np.asarray(g)
            e = heVectors[heIndices[row], :]
            e = np.asarray(((e[0], e[1]), (e[1], -e[0])))
            g = np.dot(la.inv(np.dot(g.T, g)), g.T)
            g = np.dot(g, verts2edges)
            h = - np.dot(e, g)
            rows = []
            cols = []
            for i in range(0, len(vertices)):
                rows.append(2 * row);
                cols.append(2 * vertices[i])
                rows.append(2 * row);
                cols.append(2 * vertices[i] + 1)
            for i in range(0, len(vertices)):
                rows.append(2 * row + 1);
                cols.append(2 * vertices[i])
                rows.append(2 * row + 1);
                cols.append(2 * vertices[i] + 1)

            data = h.flatten()
            Arows.extend(rows)
            Acols.extend(cols)
            Adata.extend(data)
            Grows.extend(rows)
            Gcols.extend(cols)
            Gdata.extend(g.flatten())
        spA1top = sp.csr_matrix((Adata, (Arows, Acols)), shape=(edges.size, nVertices * 2))
        spG = sp.csr_matrix((Gdata, (Grows, Gcols)), shape=(edges.size, nVertices * 2))
        return spA1top, spG

    def _buildA1bottom(self, pins, w, nVertices):
        Arows = []
        Acols = []
        Adata = []
        for row in range(0, len(pins)):
            for pin in pins[row]:
                pin_idx = pin[0]
                pin_weight = pin[1] * w
                # pin = pins[row]
                Arows.append(2 * row)
                Acols.append(2 * pin_idx)
                Adata.append(pin_weight)
                Arows.append(2 * row + 1)
                Acols.append(2 * pin_idx + 1)
                Adata.append(pin_weight)
        spA1bottom = sp.csr_matrix((Adata, (Arows, Acols)), shape=(pins.shape[0] * 2, nVertices * 2))
        return spA1bottom

    def _buildB1(self, pinPositions, w, nEdges):
        brows = range(nEdges * 2, nEdges * 2 + pinPositions.size)
        bcols = [0 for i in range(0, len(brows))]
        bdata = (w * pinPositions).flatten()
        bshape = (nEdges * 2 + pinPositions.size, 1)
        b1 = sp.csr_matrix((bdata, (brows, bcols)), shape=bshape).tolil()
        return b1

    def _buildA2top(self, edges, nVertices):
        Arow = []
        Acol = []
        Adata = []
        for row in range(0, edges.shape[0]):
            v0, v1 = edges[row, :]
            Arow.append(row);
            Acol.append(v0);
            Adata.append(-1)
            Arow.append(row);
            Acol.append(v1);
            Adata.append(1)
        shape = (edges.shape[0], nVertices)
        spA2top = sp.csr_matrix((Adata, (Arow, Acol)), shape=shape)
        return spA2top

    def _buildA2bottom(self, pins, w, nVertices):
        Arow = []
        Acol = []
        Adata = []
        for row in range(0, pins.shape[0]):
            for pin in pins[row]:
                pin_idx = pin[0]
                pin_weight = pin[1] * w
                Arow.append(row)
                Acol.append(pin_idx)
                Adata.append(pin_weight)
        shape = (pins.shape[0], nVertices)
        spA2bottom = sp.csr_matrix((Adata, (Arow, Acol)), shape=shape)
        return spA2bottom

    def _buildB2(self, heVectors, heIndices, edges, pinPoses, w, G, v1):
        T1 = G * v1
        b2 = []
        for row in range(0, edges.shape[0]):
            e0 = heVectors[heIndices[row], :]
            c = T1[2 * row];
            s = T1[2 * row + 1]
            rScale = 1.0 / np.sqrt(c * c + s * s)
            c *= rScale;
            s *= rScale
            T2 = np.asarray(((c, s), (-s, c)))
            e1 = np.dot(T2, e0)
            b2.extend(e1)
        for row in range(0, pinPoses.shape[0]):
            pinPos = pinPoses[row, :]
            b2.extend(w * pinPos)
        b2 = np.asarray(b2).reshape(-1, 2)
        return b2
    #######################
    # End ARAP functions
    #######################
