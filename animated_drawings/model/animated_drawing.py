# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import logging
import ctypes
import heapq
import math
import time
from typing import Dict, List, Tuple, Optional, TypedDict, DefaultDict
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np
import numpy.typing as npt
from skimage import measure
from shapely import geometry
from OpenGL import GL

from scipy.spatial import Delaunay
from animated_drawings.model.transform import Transform
from animated_drawings.model.time_manager import TimeManager
from animated_drawings.model.retargeter import Retargeter
from animated_drawings.model.arap import ARAP
from animated_drawings.model.joint import Joint
from animated_drawings.model.quaternions import Quaternions
from animated_drawings.model.vectors import Vectors
from animated_drawings.config import CharacterConfig, MotionConfig, RetargetConfig


class AnimatedDrawingMesh(TypedDict):
    vertices: npt.NDArray[np.float32]
    triangles: List[npt.NDArray[np.int32]]


class AnimatedDrawingsJoint(Joint):
    """ Joints within Animated Drawings Rig."""

    def __init__(self, name: str, x: float, y: float):
        super().__init__(name=name, offset=np.array([x, 1 - y, 0]))

        self.starting_theta: float
        self.current_theta: float


class AnimatedDrawingRig(Transform):
    """ The skeletal rig used to deform the character """

    def __init__(self, char_cfg: CharacterConfig):
        """ Initializes character rig.  """
        super().__init__()

        # create dictionary populated with joints
        joints_d: Dict[str, AnimatedDrawingsJoint]
        joints_d = {joint['name']: AnimatedDrawingsJoint(joint['name'], *joint['loc']) for joint in char_cfg.skeleton}

        # assign joints within dictionary as childre of their parents
        for joint_d in char_cfg.skeleton:
            if joint_d['parent'] is None:
                continue
            joints_d[joint_d['parent']].add_child(joints_d[joint_d['name']])

        # updates joint positions to reflect local offsets from their parent joints
        def _update_positions(t: Transform):
            """ Now that kinematic parent-> child chain is formed, subtract parent world positions to get actual child offsets"""
            parent: Optional[Transform] = t.get_parent()
            if parent is not None:
                offset = np.subtract(t.get_local_position(), parent.get_world_position())
                t.set_position(offset)
            for c in t.get_children():
                _update_positions(c)
        _update_positions(joints_d['root'])

        # compute the starting rotation (CCW from +Y axis) of each joint
        for _, joint in joints_d.items():
            parent = joint.get_parent()
            if parent is None:
                joint.starting_theta = 0
                continue

            v1_xy = np.array([0.0, 1.0])
            v2 = Vectors([np.subtract(joint.get_world_position(), parent.get_world_position())])
            v2.norm()
            v2_xy: npt.NDArray[np.float32] = v2.vs[0, :2]
            theta = np.arctan2(v2_xy[1], v2_xy[0]) - np.arctan2(v1_xy[1], v1_xy[0])
            theta = np.degrees(theta)
            theta = theta % 360.0
            theta = np.where(theta < 0.0, theta + 360, theta)

            joint.starting_theta = float(theta)

        # attach root joint
        self.root_joint = joints_d['root']
        self.add_child(self.root_joint)

        # cache for later
        self.joint_count = joints_d['root'].joint_count()

        # set up buffer for visualizing vertices
        self.vertices = np.zeros([2 * (self.joint_count - 1), 6], np.float32)

        self._is_opengl_initialized: bool = False
        self._vertex_buffer_dirty_bit: bool = True

    def set_global_orientations(self, bvh_frame_orientations: Dict[str, float]) -> None:
        """ Applies orientation from bvh_frame_orientation to the rig. """

        self._set_global_orientations(self.root_joint, bvh_frame_orientations)
        self._vertex_buffer_dirty_bit = True

    def get_joints_2D_positions(self) -> npt.NDArray[np.float32]:
        """ Returns array of 2D joints positions for rig.  """
        return np.array(self.root_joint.get_chain_worldspace_positions()).reshape([-1, 3])[:, :2]

    def _compute_buffer_vertices(self, parent: Optional[Transform], pointer: List[int]) -> None:
        """ Recomputes values to pass to vertex buffer. Called recursively, pointer is List[int] to emulate pass-by-reference """
        if parent is None:
            parent = self.root_joint

        for c in parent.get_children():
            p1 = c.get_world_position()
            p2 = parent.get_world_position()

            self.vertices[pointer[0], 0:3] = p1
            self.vertices[pointer[0] + 1, 0:3] = p2
            pointer[0] += 2

            self._compute_buffer_vertices(c, pointer)

    def _initialize_opengl_resources(self):
        self.vao = GL.glGenVertexArrays(1)
        self.vbo = GL.glGenBuffers(1)

        GL.glBindVertexArray(self.vao)

        # buffer vertex data
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.vertices, GL.GL_STATIC_DRAW)

        vert_bytes: int = 4 * self.vertices.shape[1]  # 4 is byte size of np.float32

        # position attributes
        pos_offset = 4 * 0
        GL.glVertexAttribPointer( 0, 3, GL.GL_FLOAT, False, vert_bytes, ctypes.c_void_p(pos_offset))
        GL.glEnableVertexAttribArray(0)

        # color attributes
        color_offset = 4 * 3
        GL.glVertexAttribPointer( 1, 3, GL.GL_FLOAT, False, vert_bytes, ctypes.c_void_p(color_offset))
        GL.glEnableVertexAttribArray(1)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        self._is_opengl_initialized = True

    def _compute_and_buffer_vertex_data(self):

        self._compute_buffer_vertices(parent=self.root_joint, pointer=[0])

        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.vertices, GL.GL_STATIC_DRAW)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        self._vertex_buffer_dirty_bit = False

    def _set_global_orientations(self, joint: AnimatedDrawingsJoint, bvh_orientations: Dict[str, float]) -> None:
        if joint.name in bvh_orientations.keys():

            theta: float = bvh_orientations[str(joint.name)] - joint.starting_theta
            theta = np.radians(theta)
            joint.current_theta = theta

            parent = joint.get_parent()
            assert isinstance(parent, AnimatedDrawingsJoint)
            if hasattr(parent, 'current_theta'):
                theta = theta - parent.current_theta

            rotation_q = Quaternions.from_angle_axis(np.array([theta]), axes=Vectors([0.0, 0.0, 1.0]))
            parent.set_rotation(rotation_q)
            parent.update_transforms()

        for c in joint.get_children():
            if isinstance(c, AnimatedDrawingsJoint):
                self._set_global_orientations(c, bvh_orientations)

    def _draw(self, **kwargs):
        if not kwargs['viewer_cfg'].draw_ad_rig:
            return

        if not self._is_opengl_initialized:
            self._initialize_opengl_resources()

        if self._vertex_buffer_dirty_bit:
            self._compute_and_buffer_vertex_data()

        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glUseProgram(kwargs['shader_ids']['color_shader'])
        model_loc = GL.glGetUniformLocation(kwargs['shader_ids']['color_shader'], "model")
        GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE, self._world_transform.T)

        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_LINES, 0, len(self.vertices))

        GL.glEnable(GL.GL_DEPTH_TEST)


class AnimatedDrawing(Transform, TimeManager):
    """
    The drawn character to be animated.
    An AnimatedDrawings object consists of four main parts:
    1. A 2D mesh textured with the original drawing, the 'visual' representation of the character
    2. A 2D skeletal rig
    3. An ARAP module which uses rig joint positions to deform the mesh
    4. A retargeting module which reposes the rig.

    After initializing the object, the retarger must be initialized by calling initialize_retarger_bvh().
    Afterwars, only the update() method needs to be called.
    """

    def __init__(self, char_cfg: CharacterConfig, retarget_cfg: RetargetConfig, motion_cfg: MotionConfig):
        super().__init__()

        self.char_cfg: CharacterConfig = char_cfg

        self.retarget_cfg: RetargetConfig = retarget_cfg

        self.img_dim: int = self.char_cfg.img_dim

        # load mask and pad to square
        self.mask: npt.NDArray[np.uint8] = self._load_mask()

        # load texture and pad to square
        self.txtr: npt.NDArray[np.uint8] = self._load_txtr()

        # generate the mesh
        self.mesh: AnimatedDrawingMesh
        self._generate_mesh()

        self.rig = AnimatedDrawingRig(self.char_cfg)
        self.add_child(self.rig)

        # perform runtime checks for character pose, modify retarget config accordingly
        self._modify_retargeting_cfg_for_character()

        self.joint_to_tri_v_idx:  Dict[str, npt.NDArray[np.int32]]
        self._initialize_joint_to_triangles_dict()

        self.indices: npt.NDArray[np.int32] = np.stack(self.mesh['triangles']).flatten()  # order in which to render triangles

        self.retargeter: Retargeter
        self._initialize_retargeter_bvh(motion_cfg, retarget_cfg)

        # initialize arap solver with original joint positions
        self.arap = ARAP(self.rig.get_joints_2D_positions(), self.mesh['triangles'], self.mesh['vertices'])

        self.vertices: npt.NDArray[np.float32]
        self._initialize_vertices()

        self._is_opengl_initialized: bool = False
        self._vertex_buffer_dirty_bit: bool = True

        # pose the animated drawing using the first frame of the bvh
        self.update()

    def _modify_retargeting_cfg_for_character(self):
        """
        If the character is drawn in particular poses, the orientation-matching retargeting framework produce poor results.
        Therefore, the retargeter config can specify a number of runtime checks and retargeting modifications to make if those checks fail.
        """
        for position_test, target_joint_name, joint1_name, joint2_name in self.retarget_cfg.char_runtime_checks:
            if position_test == 'above':
                """ Checks whether target_joint is 'above' the vector from joint1 to joint2. If it's below, removes it.
                This was added to account for head flipping when nose was below shoulders. """

                # get joints 1, 2 and target joint
                joint1 = self.rig.root_joint.get_transform_by_name(joint1_name)
                if joint1 is None:
                    msg = f'Could not find joint1 in runtime check: {joint1_name}'
                    logging.critical(msg)
                    assert False, msg
                joint2 = self.rig.root_joint.get_transform_by_name(joint2_name)
                if joint2 is None:
                    msg = f'Could not find joint2 in runtime check: {joint2_name}'
                    logging.critical(msg)
                    assert False, msg
                target_joint = self.rig.root_joint.get_transform_by_name(target_joint_name)
                if target_joint is None:
                    msg = f'Could not find target_joint in runtime check: {target_joint_name}'
                    logging.critical(msg)
                    assert False, msg

                # get world positions
                joint1_xyz = joint1.get_world_position()
                joint2_xyz = joint2.get_world_position()
                target_joint_xyz = target_joint.get_world_position()

                # rotate target vector by inverse of test_vector angle. If then below x axis discard it.
                test_vector = np.subtract(joint2_xyz, joint1_xyz)
                target_vector = np.subtract(target_joint_xyz, joint1_xyz)
                angle = math.atan2(test_vector[1], test_vector[0])
                if (math.sin(-angle) * target_vector[0] + math.cos(-angle) * target_vector[1]) < 0:
                    logging.info(f'char_runtime_check failed, removing {target_joint_name} from retargeter :{target_joint_name, position_test, joint1_name, joint2_name}')
                    del self.retarget_cfg.char_joint_bvh_joints_mapping[target_joint_name]
            else:
                msg = f'Unrecognized char_runtime_checks position_test: {position_test}'
                logging.critical(msg)
                assert False, msg

    def _initialize_retargeter_bvh(self, motion_cfg: MotionConfig, retarget_cfg: RetargetConfig):
        """ Initializes the retargeter used to drive the animated character.  """

        # initialize retargeter
        self.retargeter = Retargeter(motion_cfg, retarget_cfg)

        # validate the motion and retarget config files, now that we know char/bvh joint names
        char_joint_names: List[str] = self.rig.root_joint.get_chain_joint_names()
        bvh_joint_names = self.retargeter.bvh_joint_names
        motion_cfg.validate_bvh(bvh_joint_names)
        retarget_cfg.validate_char_and_bvh_joint_names(char_joint_names, bvh_joint_names)

        # a shorter alias
        char_bvh_root_offset: RetargetConfig.CharBvhRootOffset = self.retarget_cfg.char_bvh_root_offset

        # compute ratio of character's leg length to bvh skel leg length
        c_limb_length = 0
        c_joint_groups: List[List[str]] = char_bvh_root_offset['char_joints']
        for b_joint_group in c_joint_groups:
            while len(b_joint_group) >= 2:
                c_dist_joint = self.rig.root_joint.get_transform_by_name(b_joint_group[1])
                c_prox_joint = self.rig.root_joint.get_transform_by_name(b_joint_group[0])
                assert isinstance(c_dist_joint, AnimatedDrawingsJoint)
                assert isinstance(c_prox_joint, AnimatedDrawingsJoint)
                c_dist_joint_pos = c_dist_joint.get_world_position()
                c_prox_joint_pos = c_prox_joint.get_world_position()
                c_limb_length += np.linalg.norm(np.subtract(c_dist_joint_pos, c_prox_joint_pos))
                b_joint_group.pop(0)

        b_limb_length = 0
        b_joint_groups: List[List[str]] = char_bvh_root_offset['bvh_joints']
        for b_joint_group in b_joint_groups:
            while len(b_joint_group) >= 2:
                b_dist_joint = self.retargeter.bvh.root_joint.get_transform_by_name(b_joint_group[1])
                b_prox_joint = self.retargeter.bvh.root_joint.get_transform_by_name(b_joint_group[0])
                assert isinstance(b_dist_joint, Joint)
                assert isinstance(b_prox_joint, Joint)
                b_dist_joint_pos = b_dist_joint.get_world_position()
                b_prox_joint_pos = b_prox_joint.get_world_position()
                b_limb_length += np.linalg.norm(np.subtract(b_dist_joint_pos, b_prox_joint_pos))
                b_joint_group.pop(0)

        # compute character-bvh scale factor and send to retargeter
        scale_factor = float(c_limb_length / b_limb_length)
        projection_bodypart_group_for_offset = char_bvh_root_offset['bvh_projection_bodypart_group_for_offset']
        self.retargeter.scale_root_positions_for_character(scale_factor, projection_bodypart_group_for_offset)

        # compute the necessary orienations
        for char_joint_name, (bvh_prox_joint_name, bvh_dist_joint_name) in self.retarget_cfg.char_joint_bvh_joints_mapping.items():
            self.retargeter.compute_orientations(bvh_prox_joint_name, bvh_dist_joint_name, char_joint_name)

    def update(self):
        """
        This method receives the delta t, the amount of time to progress the character's internal time keeper.
        This method passes its time to the retargeter, which returns bone orientations.
        Orientations are passed to rig to calculate new joint positions.
        The updated joint positions are passed into the ARAP module, which computes the new vertex locations.
        The new vertex locations are stored and the dirty bit is set.
        """

        # get retargeted motion data
        frame_orientations: Dict[str, float]
        joint_depths: Dict[str, float]
        root_position: npt.NDArray[np.float32]
        frame_orientations, joint_depths, root_position = self.retargeter.get_retargeted_frame_data(self.get_time())

        # update the rig's root position and reorient all of its joints
        self.rig.root_joint.set_position(root_position)
        self.rig.set_global_orientations(frame_orientations)

        # using new joint positions, calculate new mesh vertex xy positions
        control_points: npt.NDArray[np.float32] = self.rig.get_joints_2D_positions() - root_position[:2]
        self.vertices[:, :2] = self.arap.solve(control_points) + root_position[:2]

        # use the z position of the rig's root joint for all mesh vertices
        self.vertices[:, 2] = self.rig.root_joint.get_world_position()[2]

        self._vertex_buffer_dirty_bit = True

        # using joint depths, determine the correct order in which to render the character
        self._set_draw_indices(joint_depths)

    def _set_draw_indices(self, joint_depths: Dict[str, float]):

        # sort segmentation groups by decreasing depth_driver's distance to camera
        _bodypart_render_order: List[Tuple[int, np.float32]] = []
        for idx, bodypart_group_dict in enumerate(self.retarget_cfg.char_bodypart_groups):
            bodypart_depth: np.float32 = np.mean([joint_depths[joint_name] for joint_name in bodypart_group_dict['bvh_depth_drivers']])
            _bodypart_render_order.append((idx, bodypart_depth))
        _bodypart_render_order.sort(key=lambda x: float(x[1]))

        # Add vertices belonging to joints in each segment group in the order they will be rendered
        indices: List[npt.NDArray[np.int32]] = []
        for idx, dist in _bodypart_render_order:
            intra_bodypart_render_order = 1 if dist > 0 else -1  # if depth driver is behind plane, render bodyparts in reverse order
            for joint_name in self.retarget_cfg.char_bodypart_groups[idx]['char_joints'][::intra_bodypart_render_order]:
                indices.append(self.joint_to_tri_v_idx.get(joint_name, np.array([], dtype=np.int32)))
        self.indices = np.hstack(indices)

    def _initialize_joint_to_triangles_dict(self) -> None:  # noqa: C901
        """
        Uses BFS to find and return the closest joint bone (line segment between joint and parent) to each triangle centroid.
        """
        shortest_distance = np.full(self.mask.shape, 1 << 12, dtype=np.int32)  # to nearest joint
        closest_joint_idx = np.full(self.mask.shape, -1, dtype=np.int8)  # track joint idx nearest each point

        # temp dictionary to help with seed generation
        joints_d: Dict[str, CharacterConfig.JointDict] = {}
        for joint in self.char_cfg.skeleton:
            joints_d[joint['name']] = joint
            joints_d[joint['name']]['loc'][1] = 1 - joints_d[joint['name']]['loc'][1]

        # store joint names and later reference by element location
        joint_name_to_idx: List[str] = [joint['name'] for joint in self.char_cfg.skeleton]

        # seed generation
        heap: List[Tuple[float, Tuple[int, Tuple[int, int]]]] = []  # [(dist, (joint_idx, (x, y))]
        for _, joint in joints_d.items():
            if joint['parent'] is None:  # skip root joint
                continue
            joint_idx = joint_name_to_idx.index(joint['name'])
            dist_joint_xy: List[float] = joint['loc']
            prox_joint_xy: List[float] = joints_d[joint['parent']]['loc']
            seeds_xy = (self.img_dim * np.linspace(dist_joint_xy, prox_joint_xy, num=20, endpoint=False)).round()
            heap.extend([(0, (joint_idx, tuple(seed_xy.astype(np.int32)))) for seed_xy in seeds_xy])

        # BFS search
        start_time: float = time.time()
        logging.info('Starting joint -> mask pixel BFS')
        while heap:
            distance, (joint_idx, (x, y)) = heapq.heappop(heap)
            neighbors = [(x-1, y-1), (x, y-1), (x+1, y-1), (x-1, y), (x+1, y), (x-1, y+1), (x, y+1), (x+1, y+1)]
            n_dist = [1.414, 1.0, 1.414, 1.0, 1.0, 1.414, 1.0, 1.414]
            for (n_x, n_y), n_dist in zip(neighbors, n_dist):
                n_distance = distance + n_dist
                if not 0 <= n_x < self.img_dim or not 0 <= n_y < self.img_dim:
                    continue  # neighbor is outside image bounds- ignore

                if not self.mask[n_x, n_y]:
                    continue  # outside character mask

                if shortest_distance[n_x, n_y] <= n_distance:
                    continue  # a closer joint exists

                closest_joint_idx[n_x, n_y] = joint_idx
                shortest_distance[n_x, n_y] = n_distance
                heapq.heappush(heap, (n_distance, (joint_idx, (n_x, n_y))))
        logging.info(f'Finished joint -> mask pixel BFS in {time.time() - start_time} seconds')

        # create map between joint name and triangle centroids it is closest to
        joint_to_tri_v_idx_and_dist: DefaultDict[str, List[Tuple[npt.NDArray[np.int32], np.int32]]] = defaultdict(list)
        for tri_v_idx in self.mesh['triangles']:
            tri_verts = np.array([self.mesh['vertices'][v_idx] for v_idx in tri_v_idx])
            centroid_x, centroid_y = list((tri_verts.mean(axis=0) * self.img_dim).round().astype(np.int32))
            tri_centroid_closest_joint_idx: np.int8 = closest_joint_idx[centroid_x, centroid_y]
            dist_from_tri_centroid_to_bone: np.int32 = shortest_distance[centroid_x, centroid_y]
            joint_to_tri_v_idx_and_dist[joint_name_to_idx[tri_centroid_closest_joint_idx]].append((tri_v_idx, dist_from_tri_centroid_to_bone))

        joint_to_tri_v_idx: Dict[str, npt.NDArray[np.int32]] = {}
        for key, val in joint_to_tri_v_idx_and_dist.items():
            # sort by distance, descending
            val.sort(key=lambda x: float(x[1]), reverse=True)

            # retain vertex indices, remove distance info
            val = [v[0] for v in val]

            # convert to np array and save in dictionary
            joint_to_tri_v_idx[key] = np.array(val).flatten()  # type: ignore

        self.joint_to_tri_v_idx = joint_to_tri_v_idx

    def _load_mask(self) -> npt.NDArray[np.uint8]:
        """ Load and perform preprocessing upon the mask """
        mask_p: Path = self.char_cfg.mask_p
        try:
            _mask: npt.NDArray[np.uint8] = cv2.imread(str(mask_p), cv2.IMREAD_GRAYSCALE).astype(np.uint8)
            if _mask.shape[0] != self.char_cfg.img_height:
                raise AssertionError('height in character config and mask height do not match')
            if _mask.shape[1] != self.char_cfg.img_width:
                raise AssertionError('width in character config and mask height do not match')
        except Exception as e:
            msg = f'Error loading mask {mask_p}: {str(e)}'
            logging.critical(msg)
            assert False, msg

        _mask = np.rot90(_mask, 3, )  # rotate to upright

        # pad to square
        mask = np.zeros([self.img_dim, self.img_dim], _mask.dtype)
        mask[0:_mask.shape[0], 0:_mask.shape[1]] = _mask

        return mask

    def _load_txtr(self) -> npt.NDArray[np.uint8]:
        """ Load and perform preprocessing upon the drawing image """
        txtr_p: Path = self.char_cfg.txtr_p
        try:
            _txtr: npt.NDArray[np.uint8] = cv2.imread(str(txtr_p), cv2.IMREAD_IGNORE_ORIENTATION | cv2.IMREAD_UNCHANGED).astype(np.uint8)
            _txtr = cv2.cvtColor(_txtr, cv2.COLOR_BGRA2RGBA).astype(np.uint8)
            if _txtr.shape[-1] != 4:
                raise AssertionError('texture must be RGBA')
            if _txtr.shape[0] != self.char_cfg.img_height:
                raise AssertionError('height in character config and txtr height do not match')
            if _txtr.shape[1] != self.char_cfg.img_width:
                raise AssertionError('width in character config and txtr height do not match')
        except Exception as e:
            msg = f'Error loading texture {txtr_p}: {str(e)}'
            logging.critical(msg)
            assert False, msg

        _txtr = np.rot90(_txtr, 3, )  # rotate to upright

        # pad to square
        txtr = np.zeros([self.img_dim, self.img_dim, _txtr.shape[-1]], _txtr.dtype)
        txtr[0:_txtr.shape[0], 0:_txtr.shape[1], :] = _txtr

        txtr[np.where(self.mask == 0)][:, 3] = 0  # make pixels outside mask transparent

        return txtr

    def _generate_mesh(self) -> None:
        try:
            contours: List[npt.NDArray[np.float64]] = measure.find_contours(self.mask, 128)
        except Exception as e:
            msg = f'Error finding contours for character mesh: {str(e)}'
            logging.critical(msg)
            assert False, msg

        # if multiple distinct polygons are in the mask, use largest and discard the rest
        if len(contours) > 1:
            msg = f'{len(contours)} separate polygons found in mask. Using largest.'
            logging.info(msg)
            contours.sort(key=len, reverse=True)

        outside_vertices: npt.NDArray[np.float64] = measure.approximate_polygon(contours[0], tolerance=0.25)
        character_outline = geometry.Polygon(contours[0])

        # add some internal vertices to ensure a good mesh is created
        inside_vertices_xy: List[Tuple[np.float32, np.float32]] = []
        _x = np.linspace(0, self.img_dim, 40)
        _y = np.linspace(0, self.img_dim, 40)
        xv, yv = np.meshgrid(_x, _y)
        for x, y in zip(xv.flatten(), yv.flatten()):
            if character_outline.contains(geometry.Point(x, y)):
                inside_vertices_xy.append((x, y))
        inside_vertices: npt.NDArray[np.float64] = np.array(inside_vertices_xy)

        vertices: npt.NDArray[np.float32] = np.concatenate([outside_vertices, inside_vertices]).astype(np.float32)

        """
        Create a convex hull containing the character.
        Then remove unnecessary edges by discarding triangles whose centroid
        falls outside the character's outline.
        """
        convex_hull_triangles = Delaunay(vertices)
        triangles: List[npt.NDArray[np.int32]] = []
        for _triangle in convex_hull_triangles.simplices:
            tri_vertices = np.array(
                [vertices[_triangle[0]], vertices[_triangle[1]], vertices[_triangle[2]]])
            tri_centroid = geometry.Point(np.mean(tri_vertices, 0))
            if character_outline.contains(tri_centroid):
                triangles.append(_triangle)

        vertices /= self.img_dim  # scale vertices so they lie between 0-1

        self.mesh = {'vertices': vertices, 'triangles': triangles}

    def _initialize_vertices(self) -> None:
        """
        Prepare the ndarray that will be sent to rendering pipeline.
        Later, x and y vertex positions will change, but z pos, u v texture, and rgb color won't.
        """
        self.vertices = np.zeros((self.mesh['vertices'].shape[0], 8), np.float32)

        # initialize xy positions of mesh vertices
        self.vertices[:, :2] = self.arap.solve(self.rig.get_joints_2D_positions()).reshape([-1, 2])

        # initialize texture coordiantes
        self.vertices[:, 6] = self.mesh['vertices'][:, 1]                        # u tex
        self.vertices[:, 7] = self.mesh['vertices'][:, 0]                        # v tex

        # set per-joint triangle colors
        color_set: set[Tuple[np.float32, np.float32, np.float32]] = set()
        r = g = b = np.linspace(0, 1, 4, dtype=np.float32)
        while len(color_set) < len(self.joint_to_tri_v_idx):
            color = (np.random.choice(r), np.random.choice(g), np.random.choice(b))
            color_set.add(color)
        colors: npt.NDArray[np.float32] = np.array(list(color_set), np.float32)

        for c_idx, v_idxs in enumerate(self.joint_to_tri_v_idx.values()):
            self.vertices[v_idxs, 3:6] = colors[c_idx]  # rgb colors

    def _initialize_opengl_resources(self) -> None:

        h, w, _ = self.txtr.shape

        # # initialize the texture
        self.txtr_id = GL.glGenTextures(1)
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 4)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.txtr_id)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_BASE_LEVEL, 0)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAX_LEVEL, 0)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, w, h,
                        0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, self.txtr)

        self.vao = GL.glGenVertexArrays(1)
        self.vbo = GL.glGenBuffers(1)
        self.ebo = GL.glGenBuffers(1)

        GL.glBindVertexArray(self.vao)

        # buffer vertex data
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.vertices, GL.GL_DYNAMIC_DRAW)

        # buffer element index data
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER,
                        self.indices, GL.GL_STATIC_DRAW)

        # position attributes
        GL.glVertexAttribPointer(
            0, 3, GL.GL_FLOAT, False, 4 * self.vertices.shape[1], None)
        GL.glEnableVertexAttribArray(0)

        # color attributes
        GL.glVertexAttribPointer(
            1, 3, GL.GL_FLOAT, False, 4 * self.vertices.shape[1], ctypes.c_void_p(4 * 3))
        GL.glEnableVertexAttribArray(1)

        # texture attributes
        GL.glVertexAttribPointer(
            2, 2, GL.GL_FLOAT, False, 4 * self.vertices.shape[1], ctypes.c_void_p(4 * 6))
        GL.glEnableVertexAttribArray(2)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        self._is_opengl_initialized = True

    def _rebuffer_vertex_data(self):
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.vertices, GL.GL_STATIC_DRAW)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

        # buffer element index data
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER,
                        self.indices, GL.GL_STATIC_DRAW)

        GL.glBindVertexArray(0)
        self._vertex_buffer_dirty_bit = False

    def _draw(self, **kwargs):

        if not self._is_opengl_initialized:
            self._initialize_opengl_resources()

        if self._vertex_buffer_dirty_bit:
            self._rebuffer_vertex_data()

        GL.glBindVertexArray(self.vao)

        if kwargs['viewer_cfg'].draw_ad_txtr:
            GL.glActiveTexture(GL.GL_TEXTURE0)
            GL.glBindTexture(GL.GL_TEXTURE_2D, self.txtr_id)
            GL.glDisable(GL.GL_DEPTH_TEST)

            GL.glUseProgram(kwargs['shader_ids']['texture_shader'])
            model_loc = GL.glGetUniformLocation(kwargs['shader_ids']['texture_shader'], "model")
            GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE, self._world_transform.T)
            GL.glDrawElements(GL.GL_TRIANGLES, self.indices.shape[0], GL.GL_UNSIGNED_INT, None)

            GL.glEnable(GL.GL_DEPTH_TEST)

        if kwargs['viewer_cfg'].draw_ad_color:
            GL.glDisable(GL.GL_DEPTH_TEST)

            GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
            GL.glUseProgram(kwargs['shader_ids']['color_shader'])
            model_loc = GL.glGetUniformLocation(kwargs['shader_ids']['color_shader'], "model")
            GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE, self._world_transform.T)
            GL.glDrawElements(GL.GL_TRIANGLES, self.indices.shape[0], GL.GL_UNSIGNED_INT, None)

            GL.glEnable(GL.GL_DEPTH_TEST)

        if kwargs['viewer_cfg'].draw_ad_mesh_lines:
            GL.glDisable(GL.GL_DEPTH_TEST)

            GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
            GL.glUseProgram(kwargs['shader_ids']['color_shader'])
            model_loc = GL.glGetUniformLocation(kwargs['shader_ids']['color_shader'], "model")
            GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE, self._world_transform.T)

            color_black_loc = GL.glGetUniformLocation(kwargs['shader_ids']['color_shader'], "color_black")
            GL.glUniform1i(color_black_loc, 1)
            GL.glDrawElements(GL.GL_TRIANGLES, self.indices.shape[0], GL.GL_UNSIGNED_INT, None)
            GL.glUniform1i(color_black_loc, 0)

            GL.glEnable(GL.GL_DEPTH_TEST)

        GL.glBindVertexArray(0)
