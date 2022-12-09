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
import triangle
from sketch_animate.util import normalized, angle_from, rotate, translate, read_texture, scale
from sketch_animate.util import point_in_triangle
from sketch_animate.util import get_arap_handles_visibility, get_sketch_mesh_visibility, get_arap_sketch_visibility
from sketch_animate.util import bone_colors, colors, squared_distance_between_point_and_line, segment_names, x_ax
from typing import Dict
from collections import deque
import logging
from shapely.geometry import Point, Polygon

import scipy.sparse as sp
import scipy.sparse.linalg as spla
import scipy.linalg as la

from sketch_animate.DataStructures import halfedge

from sketch_animate.Shapes.Shapes import Rectangle

from PIL import Image
import cv2

from collections import defaultdict


from sketch_animate.Shapes.BaseSketch import BaseSketch



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

            color = (255, 0, 0)
            self.widget = Rectangle(color=color)
            self.dim = dim
            self.pjoint = pjoint  # the parent joint of the joint this handle corresponds to
            self.joint = joint  # the joint this handle corresponds to

            self.arap_sketch = arap_sketch  # needed so we can apply it's model transform to handles for viewing

            self.cx, self.cy = None, None
            self.set_world_coords()

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


            self.djoint = self.arap_handle.joint
            self.pjoint = self.arap_handle.pjoint

            self.points = np.zeros([2, 6], dtype=np.float32)
            self.points[:, 3:] = colors[idx]
            self.dj_loc = None
            self.pj_loc = None

            self.vao = None
            self.vbo = None
            self._initialize_opengl()



            self.update_position()


        def _initialize_opengl(self):
            self.vao = GL.glGenVertexArrays(1)
            self.vbo = GL.glGenBuffers(1)

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

        mask_path = os.path.abspath(self.sketch['image_loc'][:-4] + '_mask.png')
        if not os.path.exists(mask_path):
            assert False, 'Couldn\'t find mask file: {}'.format(mask_path)
        self.mask = Image.open(mask_path)

        # ensure joint positions that are very close to mask are over mask
        # It can be hard to get joints directly over a stick figure arm.
        self._slightly_move_image_coords_into_mask()

        attempt = 0
        while attempt < 10:
            self.triangle_mesh = None  # dictionary with mesh generated by Triangle from self.mask
            self._generate_mesh(attempt)

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

            # if the following matrix, necessary for ARAP, is singular, we slightly adjust the mask and redo the previous steps.
            # Try 10 times. If we can't get a non-singular matrix by then, give up
            if linalg.det(self.tA1 * self.A1.todense()) != 0.0:
                logging.info(f'Attempt {attempt} succeeded, ARAP matrix is not singular. Proceeding')
                break
            else:
                logging.info(f'Attempt {attempt} failed, ARAP matrix is singular. Retrying')
                attempt += 1
        else:
            logging.critical(f'Attempt {attempt} failed, cannot create non singular matrix.')
            assert False, f'Could not create non-singular matrix'
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

        for bone in ret.bones:
            bone._initialize_opengl()

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

    def draw_render_mp(self, mesh_vertices, **kwargs):
        """Drawing function, specifically for multiprocessing use while rendering
        mesh_vertices: the mesh vertices of character for this frame. precomputed in separate thread
        """
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)  # buffer vertex data
        GL.glBufferData(GL.GL_ARRAY_BUFFER, mesh_vertices, GL.GL_DYNAMIC_DRAW)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        GL.glBindVertexArray(self.vao)

        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.tex_id)

        # render the sketch texture
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        GL.glUseProgram(kwargs['shader_ids']['texture_shader'])
        model_loc = GL.glGetUniformLocation(kwargs['shader_ids']['texture_shader'], "model")
        GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE, self.model.T)

        for bone_idx, _, _ in self.render_order:
            if bone_idx not in self.indices_info.keys():
                continue
            start, length = self.indices_info[bone_idx]
            GL.glDrawElements(GL.GL_TRIANGLES, length, GL.GL_UNSIGNED_INT, ctypes.c_void_p(4 * start))

        GL.glBindVertexArray(0)

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

        # # render the sketch texture
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

        # if get_sketch_segment_visibility():
        #     GL.glUseProgram(kwargs['shader_ids']['color_shader'])
        #     model_loc = GL.glGetUniformLocation(kwargs['shader_ids']['color_shader'], "model")
        #     GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE, self.model.T)
        #     for b in self.bones:
        #         b.draw(**kwargs)

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

    def _generate_mesh(self, attempt):
        """
        Generate the character mesh using Triangle, give the character mask.
        If attempt >0, try randomly permuting the mask slightly to avoid getting a singular matrix
        """

        mask_ar = np.array(self.mask)[:, :, -1]

        if attempt > 0:
            _, cols = np.where(mask_ar == 255) # get columns where there is mask
            row = 0
            while row == 0:
                col = random.choice(cols)  # randomly choose a column
                row = np.where(mask_ar[:, col] == 255)[0][0]  # choose the pixel above highest mask pixel in column...
                if row == 0:  # ensure we don't add a border pixel to the character
                    continue
                mask_ar[row - 1, col] = 255  # and add it to mask

        contours = measure.find_contours(mask_ar, 128)
        contour = []

        # if multiple contours found, use the largest
        max_idx, max_len = -1, 0
        for idx, c in enumerate(contours):
            if len(c) > max_len:
                max_len = len(c)
                max_idx = idx
        assert max_idx != -1

        step = 15  # grab every `step` points along contour to connect. otherwise, mesh has too much detail/vertices
        try:  # img is rectangle
            for idx in range(0, len(contours[max_idx]), step):
                contour.append((contours[max_idx][idx][1] / self.dim[1], contours[max_idx][idx][0] / self.dim[0]))
        except TypeError:  # img is square
            for idx in range(0, len(contours[max_idx]), step):
                contour.append((contours[max_idx][idx][1] / self.dim, contours[max_idx][idx][0] / self.dim))
        contour = np.asarray(contour)

        ### must ensure that the contour will contain the ARAP handles
        ### iterate through the ARAP handles. First, move them into mask if they are close but not on it.
        ### next, for those that are now on mask, check to see if contour includes them. if not, expand contour
        ### to include them

        ###################### dev start ######################

        # viz = np.zeros(mask_ar.shape)

        # c = contour

        # for idx in range(len(c)):
        #     x, y = c[idx]
        #     viz[int(x * self.dim), int(y * self.dim)] = 255

        # after 'simplifying' mask by taking every `step` points, some ARAP handles may now be outside mask.
        # check this and, if so, move closest point within contour to location of ARAP handle to fix.
        poly = Polygon(contour)
        for name in self.joints.keys():
            joint = [int(x) for x in self.joints[name].loc * self.dim]
            joint = np.array([joint[0] / 400, 1 - (joint[1] / 400)])
            p = Point(joint)

            # viz[int(joint[0] * self.dim), int(joint[1] * self.dim)] = 255

            if not p.within(poly):
                node = np.array([joint[0], joint[1]])  # ARAP handle loc
                dist_2 = np.sum((contour - node)**2, axis=1)
                contour[np.argmin(dist_2)] = node

        #poly = Polygon(contour)
        #print(f'{name}: {p.within(poly)}')
        #cv2.imwrite('test.png', viz)

        ###################### dev end ######################
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
        mask_np = cv2.imread(self.sketch['image_loc'][:-4] + '_mask.png')
        mask_np = mask_np[:,:,0].astype(np.bool)

        closest_bone = np.empty(mask_np.shape[:2], dtype=np.int)  #instead of distances for each bone, just keep track of closest bone for each pixel
        in_queue = np.zeros(mask_np.shape[0:2], dtype=np.bool)  # keep track of what's in our queue

        #uncomment parts about viz if you want to see how mesh is assigned to different bones
        #viz = np.zeros((*mask_np.shape[:2], 3), dtype='uint8')
        #COLOR = [
        #    [255, 0, 0],
        #    [0, 255, 0],
        #    [0, 0, 255],
        #    [255, 0, 255],
        #    [0, 255, 255],
        #    [255, 0, 255],
        #    [128, 0, 255],
        #    [0, 128, 255],
        #    [255, 0, 128],
        #    [255, 0, 128],
        #    [0, 128, 255],
        #    [128, 0, 255],
        #    [255, 0, 0],
        #    [0, 255, 0],
        #    [0, 0, 255]
        #]

        seeds = []
        queue = deque()
        for bone_idx, bone in enumerate(self.bones):  # for each bone
            joint_img_coord1 = [bone.djoint.loc[0], 1 - bone.djoint.loc[1]]  # coordindates of bone first joint
            y1 = int(joint_img_coord1[0] * mask_np.shape[0])
            x1 = int(joint_img_coord1[1] * mask_np.shape[1])

            joint_img_coord2 = [bone.pjoint.loc[0], 1 - bone.pjoint.loc[1]]  # coordinates of bone second joint
            y2 = int(joint_img_coord2[0] * mask_np.shape[0])
            x2 = int(joint_img_coord2[1] * mask_np.shape[1])

            for _p in range(0, 20):  # sample 20 points along each bone
                p = _p / 20
                point = int(round(x1 + p * (x2-x1))),  int(round(y1 + p * (y2 - y1))), bone_idx
                seeds.append(point)
            seeds = list(set(seeds))  # dedup

            for seed in seeds:  #
                closest_bone[seed[0], seed[1]] = seed[2]
                queue.append(seed)
                in_queue[seed[0], seed[1]] = True
                #viz[seed[0], seed[1]] = [255, 255, 255]

        while queue:  # while items in queue
            x, y, bone_idx = queue.popleft()  # get first item
            for _x, _y in [(x - 1, y - 1), (x + 0, y - 1), (x + 1, y - 1),  # for each possible neighbor
                           (x - 1, y + 0), (x + 1, y + 0),
                           (x - 1, y + 1), (x + 0, y + 1), (x + 1, y + 1)]:

                if in_queue[_x, _y] or not mask_np[_x, _y]:  # if it's already in queue or outside mask,
                    continue
                queue.append((_x, _y, bone_idx))  # otherwise append it..
                in_queue[_x, _y] = True
                closest_bone[_x, _y] = bone_idx
                #viz[_x, _y] = COLOR[bone_idx]
        #cv2.imwrite('/Users/hjessmith/Desktop/viz.png', viz)

        self.tri2bone = {}
        # for each triangle, get centroid and use it to find closest bone
        for idx, t in enumerate(self.triangle_mesh['triangles']):
            _v0, _v1, _v2 = self.triangle_mesh['vertices'][t[0:3]]
            v0 = [int(_v0[0] * mask_np.shape[0]), int((_v0[1]) * mask_np.shape[1])]
            v1 = [int(_v1[0] * mask_np.shape[0]), int((_v1[1]) * mask_np.shape[1])]
            v2 = [int(_v2[0] * mask_np.shape[0]), int((_v2[1]) * mask_np.shape[1])]
            centroid_x, centroid_y = int((v0[0] + v1[0] + v2[0]) / 3), int((v0[1] + v1[1] + v2[1]) / 3)
            closest_bone_idx = closest_bone[centroid_y, centroid_x]
            self.tri2bone[idx] = closest_bone_idx

    def _slightly_move_image_coords_into_mask(self, distance_to_move=20):
        assert type(self.dim) == int, f'self.dim is not an int'

        for name in self.joints.keys():
            image_coords = [self.joints[name].loc[0], 1 - self.joints[name].loc[1]]

            x = int(round(image_coords[0]*self.dim))
            y = int(round(image_coords[1]*self.dim))
            mask = np.array(self.mask).T[0,:,:]

            # if predicted joint is outside of mask dimensions return
            if not (0 <= x < self.dim and 0 <= y < self.dim):
                continue

            # if joint is inside mask, don't adjust it
            if mask[x, y] == 255:
                continue

            # otherwise, BFS search to find a point in mask that is within 10 pixels of joint location
            queue = deque()
            queue.append( (x, y, 0) )
            explored = [(x, y)]

            while queue:
                x, y, distance = queue.popleft()  # get first item
                for _x, _y in [                (x + 0, y - 1),                  # for each possible neighbor
                               (x - 1, y + 0),                 (x + 1, y + 0),
                                               (x + 0, y + 1),               ]:

                    # if outside the image
                    if not (0 <= _x < self.dim and 0 <= _y < self.dim):
                        continue

                    # if we've already seen this
                    if (_x, _y) in explored:
                        continue

                    # if we've already searched the alloted distance
                    if distance >= distance_to_move:
                        continue

                    # if inside the mask, return the new locations
                    if mask[x, y] == 255:
                        self.joints[name].loc = np.array([_x / self.dim, 1 - _y/self.dim], dtype=np.float32)
                        queue = None
                        break

                    # otherwise, add to queue
                    queue.append((_x, _y, distance+1))
                    explored.append((_x, _y))
            else:
                # if search failed, return original image coordinates
                logging.info(f'Could not find point on mask within {distance} pixels for {name}')

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

            image_coords = [self.joints[name].loc[0], 1 - self.joints[name].loc[1]]

            # If the keypoint lies close to but not directly over the mask, adjust so that it does.
            # image_coords = self._slightly_move_image_coords_into_mask(image_coords, 20, name)

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
    def _arap_solve_render_mp(self):

        self._update_global_matrices()
        for arap_handle in self.arap_handles:
            arap_handle.set_world_coords()

        self.pinPoses = []
        for handle in self.arap_handles:
            self.pinPoses.append((handle.cx, 1 - handle.cy))
        self.pinPoses = np.asarray(self.pinPoses)

        b1 = self._buildB1(self.pinPoses, self.w, self.nEdges)
        v1 = spla.spsolve(self.tA1xA1, self.tA1 * b1)

        b2 = self._buildB2(self.heVectors, self.heIndices, self.edges, self.pinPoses, self.w, self.G, v1)
        v2x = spla.spsolve(self.tA2xA2, self.tA2 * b2[:, 0])
        v2y = spla.spsolve(self.tA2xA2, self.tA2 * b2[:, 1])
        v2 = np.vstack((v2x, v2y)).T

        for idx in range(self.mesh_vertices.shape[0]):
            self.mesh_vertices[idx, 0] = v2[idx][0]
            self.mesh_vertices[idx, 1] = 1 - v2[idx][1]

        return self.mesh_vertices.copy()

    def _arap_solve(self):

        self.pinPoses = []
        for handle in self.arap_handles:
            self.pinPoses.append((handle.cx, 1 - handle.cy))
        self.pinPoses = np.asarray(self.pinPoses)

        b1 = self._buildB1(self.pinPoses, self.w, self.nEdges)
        v1 = spla.spsolve(self.tA1xA1, self.tA1 * b1)

        b2 = self._buildB2(self.heVectors, self.heIndices, self.edges, self.pinPoses, self.w, self.G, v1)
        v2x = spla.spsolve(self.tA2xA2, self.tA2 * b2[:, 0])
        v2y = spla.spsolve(self.tA2xA2, self.tA2 * b2[:, 1])
        v2 = np.vstack((v2x, v2y)).T

        for idx in range(self.mesh_vertices.shape[0]):
            self.mesh_vertices[idx, 0] = v2[idx][0]
            self.mesh_vertices[idx, 1] = 1 - v2[idx][1]

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
        self.A1top, self.G = self._buildA1top(self.heVectors, self.halfedges, self.edges, self.heIndices, self.nVertices)
        self.A1bottom = self._buildA1bottom(self.pins, self.w, self.nVertices)

        self.A1 = sp.vstack((self.A1top, self.A1bottom))
        self.tA1 = self.A1.transpose()
        self.tA1xA1 = self.tA1 * self.A1

        self.A2top = self._buildA2top(self.edges, self.nVertices)
        self.A2bottom = self._buildA2bottom(self.pins, self.w, self.nVertices)

        self.A2 = sp.vstack((self.A2top, self.A2bottom))
        self.tA2 = self.A2.transpose()
        self.tA2xA2 = self.tA2 * self.A2

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
        b1 = sp.csr_matrix((bdata, (brows, bcols)), shape=bshape)
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
