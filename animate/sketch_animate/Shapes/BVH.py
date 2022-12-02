import OpenGL.GL as GL
import numpy as np
import ctypes

import sketch_animate.motion.BVH as holden_BVH
from sketch_animate.motion.Animation import positions_global

from sklearn.decomposition import PCA

from sketch_animate.util import rotate, translate, x_ax, z_ax, y_ax, normalized, angle_between


class BVH:

    def __init__(self, cfg):
        self.cfg = cfg
        self.filename = self.cfg['BVH_PATH']

        self.jnt_map, self.scaling_factor = get_jnt_map_and_scale(self.filename)

        self._animation, self.joint_names, self.frametime = holden_BVH.load(self.filename)
        self.frame_count = self._animation.shape[0]
        self.parents = self._animation.parents

        self.pos = positions_global(self._animation)  # nd.array: shape = (frames, joints, 3)
        self.model = np.identity(4, np.float32)
        self._rescale_and_reposition_bvh()

        self.vao = GL.glGenVertexArrays(1)
        self.vbo = GL.glGenBuffers(1)
        self.ebo = GL.glGenBuffers(1)

        GL.glBindVertexArray(self.vao)

        self.indices = []
        self._compute_and_buffer_skeleton_element_indices()

        points_shape = [self.pos.shape[0] * self.pos.shape[1], 6]
        self.points = np.zeros(points_shape, dtype=np.float32)  # [frame, joint, vertexdata(xyz + rgb)
        self._compute_and_buffer_vertices()

        self._set_attributes()

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        self.pc_centroids = []
        self.pcs = []
        self.pca_vaos = []
        self.pca_vbos = []
        # self.calculate_PCA()

    def _rescale_and_reposition_bvh(self):
        self.pos /= self.scaling_factor  # scale it down

        # translate so that first frame has the root at the origin
        offset = self.get_global_joint_position('root', 0)
        self.pos -= offset

        # rotate everything so that the skeleton is facing upwards in the first frame
        # for the time being, we're just going to assume that Z is up in the BVH, though in our software it is Y
        # rotate(y_ax, 90)
        if get_bvh_up_dir(self.filename) is 'z':  # y is up here
            _pos = self.pos.copy()
            _pos = np.zeros((self.pos.shape[0], self.pos.shape[1], 4, 4))
            _pos[:, :, 0:3, -1] = self.pos
            for idx in range(0, 4):
                _pos[:, :, idx, idx] = 1.0

            r_mat = np.expand_dims(rotate(z_ax, 90.0) @ rotate(y_ax, 90.0), [0, 1])

            self.pos = (r_mat @ _pos)[:, :, :-1, -1]

    def calculate_PCA_from_joint_list(self, joint_list, window_len=100):
        """
        given a set of joint names, this computes a PCA on a window of joint positions and returns information
        necessary for positioning the camera at each time step
        :return: (pc_centroids, pcs, pca_vao, pca_vbo), where
        pc_centroids: N x 2 x 3 ndarray - mean joint position for joints over entire window (where camera should be pointing)
        pcs: N x 3 x 3 ndarray - principal components
        """

        for i in range(
                3):  # if the model is rotated, the principal components won't line up correctly TODO fix this hack
            for j in range(3):
                if i == j:
                    assert self.model[i, j] == 1
                else:
                    assert self.model[i, j] == 0

        joint_idxs = [self.joint_names.index(self.jnt_map[joint]) for joint in joint_list]
        # lwrist_idx = self.joint_names.index(self.jnt_map['left_hand'])
        # lelbow_idx = self.joint_names.index(self.jnt_map['left_elbow'])
        # lshldr_idx = self.joint_names.index(self.jnt_map['left_shoulder'])
        # joint_idxs = [lwrist_idx, lelbow_idx, lshldr_idx]

        root_idx = self.joint_names.index(self.jnt_map['root'])

        frame_count = self.pos.shape[0]

        pcs = np.zeros([frame_count, 6, 3], np.float32)
        pc_centroid = np.zeros([frame_count, 3], np.float32)
        for frame in range(frame_count):
            lower = int(max(0, frame - window_len / 2))
            upper = int(min(frame_count, frame + window_len / 2))
            window_pos = self.pos[lower:upper, joint_idxs, :]

            _mean = list(np.mean(window_pos, axis=(0, 1))) + [1.0]
            _mean = self.model @ _mean
            pc_centroid[frame] = _mean[0:-1]

            window_pos -= np.expand_dims(self.pos[lower:upper, root_idx, :],
                                         axis=1)  # pc should be computed based on motion of limbs in root, not global, space
            pca = PCA(n_components=3)
            pca.fit(np.reshape(window_pos, [-1, 3]))
            pcs[frame, [1, 3, 5]] = normalized(pca.components_[0]), normalized(pca.components_[1]), normalized(
                pca.components_[2])

        # ensure components don't flip
        for frame in range(1, frame_count):
            pc1_p, pc2_p, pc3_p = pcs[frame - 1, [1, 3, 5]]  # previous pcs
            pc1, pc2, pc3 = pcs[frame, [1, 3, 5]]
            pc1_i, pc2_i, pc3_i = -pc1, -pc2, -pc3

            angle1 = angle_between(pc1_p, pc1)
            angle1_i = angle_between(pc1_p, pc1_i)

            if abs(angle1_i) < abs(angle1):
                pcs[frame, 1] = pc1_i

            angle2 = angle_between(pc2_p, pc2)
            angle2_i = angle_between(pc2_p, pc2_i)

            if abs(angle2_i) < abs(angle2):
                pcs[frame, 3] = pc2_i

            angle3 = angle_between(pc3_p, pc3)
            angle3_i = angle_between(pc3_p, pc3_i)

            if abs(angle3_i) < abs(angle3):
                pcs[frame, 5] = pc3_i

        # pcs = np.squeeze(np.reshape(pcs, [-1, 1, 3]), 1)

        pca_vao = GL.glGenVertexArrays(1)
        pca_vbo = GL.glGenBuffers(1)

        GL.glBindVertexArray(pca_vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, pca_vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, np.squeeze(np.reshape(pcs, [-1, 1, 3]), 1), GL.GL_STATIC_DRAW)

        # position attributes
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 4 * pcs.shape[-1], None)
        GL.glEnableVertexAttribArray(0)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        self.pcs.append(pcs)
        self.pc_centroids.append(pc_centroid)
        self.pca_vaos.append(pca_vao)
        self.pca_vbos.append(pca_vbo)

        return pc_centroid, pcs[:, -1]  # return centroid and last principal component

    def _recompute_points_for_use_without_element_array(self):
        _points = np.empty([self.indices.shape[0] * self.indices.shape[1], self.points.shape[1]], np.float32)
        for idx, element in enumerate(self.indices):
            start = idx * len(element)
            end = start + len(element)
            _points[start:end] = self.points[element]
        self.points = _points
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.points, GL.GL_STATIC_DRAW)

    def _compute_and_buffer_vertices(self):
        frame_count, joint_count = self.pos.shape[:2]
        for frame_idx in range(frame_count):
            frame_start = frame_idx * joint_count
            frame_end = frame_start + joint_count

            if self.cfg['CENTER_BVH_AT_ORIGIN']:
                adjustment = self.pos[frame_idx, 0,
                             :3]  # adjust by subtracting XZ coodinates of root from everything each frame
                adjustment[1] = 0.0
            elif self.cfg['REPOSITION_BVH'] is not None:
                adjustment = np.array([self.cfg['REPOSITION_BVH']], np.float32)
            else:
                adjustment = np.zeros([3], np.float32)

            self.points[frame_start:frame_end, :3] = self.pos[frame_idx, :, :3] - adjustment
            self.points[frame_start:frame_end, 3] = 1.0  # make the lines red

        # because opengl macbookpro isn't working with element arrays, recompute points
        self._recompute_points_for_use_without_element_array()
        # buffer vertex data
        # GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        # GL.glBufferData(GL.GL_ARRAY_BUFFER, self.points, GL.GL_STATIC_DRAW)

    def _compute_and_buffer_skeleton_element_indices(self):
        for c_id, p_id in enumerate(self.parents):  # child id, parent id
            if p_id == -1:
                continue
            self.indices.append(c_id)
            self.indices.append(p_id)

        self.indices = np.array([self.indices], np.uint)
        self.indices = np.repeat(self.indices, self.pos.shape[0], axis=0)
        frame_count = self.pos.shape[0]
        joint_count = self.pos.shape[1]
        for frame in range(frame_count):
            offset = frame * joint_count
            self.indices[frame] += offset

        # buffer element index data
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.indices, GL.GL_STATIC_DRAW)

    def _set_attributes(self):
        # position attributes
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 4 * self.points.shape[1], None)
        GL.glEnableVertexAttribArray(0)

        # color attributes
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, False, 4 * self.points.shape[1], ctypes.c_void_p(4 * 3))
        GL.glEnableVertexAttribArray(1)

    def get_root_position(self, time: int):
        root_pos = self.model @ np.array([*self.pos[time, 0, :], 1.0], np.float32)
        return root_pos[0:3]

    def get_global_joint_position(self, jnt_name: str, frame: int):
        jnt_idx = self.joint_names.index(self.jnt_map[jnt_name])
        jnt_pos = (self.model @ np.array([*self.pos[frame, jnt_idx, :], 1.0], np.float32))[0:3]
        return jnt_pos

    def get_forward(self, frame_idx: int):

        l1 = self.get_global_joint_position('left_hip', frame_idx)
        r1 = self.get_global_joint_position('right_hip', frame_idx)
        l2 = self.get_global_joint_position('left_shoulder', frame_idx)
        r2 = self.get_global_joint_position('right_shoulder', frame_idx)

        left = np.subtract(r1, l1) + np.subtract(r2, l2)
        forward = np.array([left[2], 0, -left[0]], np.float32)
        return forward

    def draw(self, **kwargs):
        GL.glUseProgram(kwargs['shader_ids']['bvh_shader'])

        model_loc = GL.glGetUniformLocation(kwargs['shader_ids']['bvh_shader'], "model")
        GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE, self.model.T)

        frame_num_loc = GL.glGetUniformLocation(kwargs['shader_ids']['bvh_shader'], "frame_num")
        GL.glUniform1i(frame_num_loc, kwargs['time'])

        joint_num_loc = GL.glGetUniformLocation(kwargs['shader_ids']['bvh_shader'], "joint_num")

        # switching this up because element array isn't working
        # GL.glUniform1i(joint_num_loc, len(self.joint_names))
        GL.glUniform1i(joint_num_loc, len(self.joint_names) * 2 - 2)  # -2 because we don't draw a root segment

        GL.glBindVertexArray(self.vao)

        # GL.glDrawElements(GL.GL_LINES, self.pos.shape[0] * self.pos.shape[1] * 2, GL.GL_UNSIGNED_INT, None)
        GL.glDrawArrays(GL.GL_LINES, 0, self.pos.shape[0] * self.pos.shape[1] * 2)

        ##############################################
        ##############################################
        ##############################################

        GL.glUseProgram(kwargs['shader_ids']['pointcloud_shader'])

        model_loc = GL.glGetUniformLocation(kwargs['shader_ids']['pointcloud_shader'], "model")
        GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE, self.model.T)

        joint_num_loc = GL.glGetUniformLocation(kwargs['shader_ids']['pointcloud_shader'], "joint_num")
        GL.glUniform1i(joint_num_loc, len(self.joint_names) * 2 - 2)  # -2 because we don't draw a root segment

        frame_num_loc = GL.glGetUniformLocation(kwargs['shader_ids']['pointcloud_shader'], "frame_num")
        GL.glUniform1i(frame_num_loc, kwargs['time'])

        # GL.glDrawArrays(GL.GL_POINTS, 0, self.pos.shape[0] * self.pos.shape[1] * 2)

        ##############################################
        ##############################################
        ##############################################
        GL.glUseProgram(kwargs['shader_ids']['vector_shader'])

        if self.cfg['DRAW_BVH_PCS']:
            for idx, _ in enumerate(self.pca_vaos):
                pca_vao = self.pca_vaos[idx]
                pc_centroid = self.pc_centroids[idx][kwargs['time']]

                GL.glBindVertexArray(pca_vao)
                frame_num_loc = GL.glGetUniformLocation(kwargs['shader_ids']['vector_shader'], "frame_num")
                GL.glUniform1i(frame_num_loc, kwargs['time'])

                pc_centroid_loc = GL.glGetUniformLocation(kwargs['shader_ids']['vector_shader'], "pc_centroid")
                GL.glUniform3fv(pc_centroid_loc, 1, pc_centroid)

                first_vertex = kwargs['time'] * 6
                GL.glDrawArrays(GL.GL_LINES, first_vertex, 6)

                GL.glBindVertexArray(0)


#####################
# Below are mappings and functions to deal with different BVH skeletons
#####################
sst_jnt_map = {  # map from sketch skeleton joints to bvh joints
    'neck': 'thorax',
    'head': 'head',
    'torso': 'pelvis',
    'root': 'root',
    'right_shoulder': 'rhumerus',
    'right_elbow': 'rradius',
    'right_hand': 'rhand',
    'left_shoulder': 'lhumerus',
    'left_elbow': 'lradius',
    'left_hand': 'lhand',
    'right_hip': 'rfemur',
    'right_knee': 'rtibia',
    'right_foot': 'rfoot',
    'left_hip': 'lfemur',
    'left_knee': 'ltibia',
    'left_foot': 'lfoot',
}

cmu_jnt_map = {
    'neck': 'Chest2',
    'head': 'Head',
    'torso': 'Hips',
    'root': 'Hips',
    'right_shoulder': 'RightShoulder',
    'right_elbow': 'RightElbow',
    'right_hand': 'RightWrist',
    'left_shoulder': 'LeftShoulder',
    'left_elbow': 'LeftElbow',
    'left_hand': 'LeftWrist',
    'right_hip': 'RightHip',
    'right_knee': 'RightKnee',
    'right_foot': 'RightToe',
    'left_hip': 'LeftHip',
    'left_knee': 'LeftKnee',
    'left_foot': 'LeftToe',
}

cmu_new_jnt_map = {
    'neck': 'Neck',
    'head': 'Head',
    'torso': 'Hips',
    'root': 'Hips',
    'right_shoulder': 'RightArm',
    'right_elbow': 'RightForeArm',
    'right_hand': 'RightHand',
    'left_shoulder': 'LeftArm',
    'left_elbow': 'LeftForeArm',
    'left_hand': 'LeftHand',
    'right_hip': 'RightUpLeg',
    'right_knee': 'RightLeg',
    'right_foot': 'RightFoot',
    'left_hip': 'LeftUpLeg',
    'left_knee': 'LeftLeg',
    'left_foot': 'LeftFoot',
}

cmu_new2_jnt_map = {
    'neck': 'thorax',
    'head': 'head',
    'torso': 'pelvis',
    'root': 'pelvis',
    'right_shoulder': 'rhumerus',
    'right_elbow': 'rradius',
    'right_hand': 'rhand',
    'left_shoulder': 'lhumerus',
    'left_elbow': 'lradius',
    'left_hand': 'lhand',
    'right_hip': 'rfemur',
    'right_knee': 'rtibia',
    'right_foot': 'rfoot',
    'left_hip': 'lfemur',
    'left_knee': 'ltibia',
    'left_foot': 'lfoot',
}

cmu_new3_jnt_map = {
    'neck': 'LowerNeck',
    'head': 'Neck',
    'torso': 'pelvis',
    'root': 'pelvis',
    'right_shoulder': 'rhumerus',
    'right_elbow': 'rradius',
    'right_hand': 'rhand',
    'left_shoulder': 'lhumerus',
    'left_elbow': 'lradius',
    'left_hand': 'lhand',
    'right_hip': 'rfemur',
    'right_knee': 'rtibia',
    'right_foot': 'rfoot',
    'left_hip': 'lfemur',
    'left_knee': 'ltibia',
    'left_foot': 'lfoot',
}

cmu_1006_jnt_map = {
    'neck': 'Neck',
    'head': 'Head',
    'torso': 'Spine3',
    'root': 'Hips',
    'right_shoulder': 'RightArm',
    'right_elbow': 'RightForeArm',
    'right_hand': 'RightHand',
    'left_shoulder': 'LeftArm',
    'left_elbow': 'LeftForeArm',
    'left_hand': 'LeftHand',
    'right_hip': 'RightUpLeg',
    'right_knee': 'RightLeg',
    'right_foot': 'RightFoot',
    'left_hip': 'LeftUpLeg',
    'left_knee': 'LeftLeg',
    'left_foot': 'LeftFoot',
}

tcd_jnt_map = {
    'neck': 'Neck',
    'head': 'Head',
    'torso': 'Spine3',
    'root': 'root',
    'right_shoulder': 'RightShoulder',
    'right_elbow': 'RightForeArm',
    'right_hand': 'RightHand',
    'left_shoulder': 'LeftShoulder',
    'left_elbow': 'LeftForeArm',
    'left_hand': 'LeftHand',
    'right_hip': 'RightUpLeg',
    'right_knee': 'RightLeg',
    'right_foot': 'RightFoot',
    'left_hip': 'LeftUpLeg',
    'left_knee': 'LeftLeg',
    'left_foot': 'LeftFoot',
}

mixamo_jnt_map = {
    'neck': 'Neck',
    'head': 'Head',
    'torso': 'Spine2',
    'root': 'Hips',
    'right_shoulder': 'RightArm',
    'right_elbow': 'RightForeArm',
    'right_hand': 'RightHand',
    'left_shoulder': 'LeftArm',
    'left_elbow': 'LeftForeArm',
    'left_hand': 'LeftHand',
    'right_hip': 'RightUpLeg',
    'right_knee': 'RightLeg',
    'right_foot': 'RightFoot',
    'left_hip': 'LeftUpLeg',
    'left_knee': 'LeftLeg',
    'left_foot': 'LeftFoot',
}


def get_jnt_map_and_scale(filename):
    parent_dir = filename.split('/')[-2]
    if parent_dir == 'sst':
        return sst_jnt_map, 100
    elif parent_dir == 'cmu':
        return cmu_jnt_map, 25
    elif parent_dir == 'tcd':
        return tcd_jnt_map, 100
    elif parent_dir == 'cmu_new':
        return cmu_new_jnt_map, 100
    elif parent_dir == 'cmu_new2':
        return cmu_new2_jnt_map, 100
    elif parent_dir == 'cmu_new3':
        return cmu_new3_jnt_map, 100
    elif parent_dir in ['cmu_1006', '5yr_old', '8yr_old']:
        return cmu_1006_jnt_map, 100
    elif parent_dir == 'mixamo':
        return mixamo_jnt_map, 100
    else:
        assert False, "unrecognized parent directory for file: {}".format(filename)


def get_bvh_up_dir(filename):
    parent_dir = filename.split('/')[-2]
    if parent_dir in ['cmu_new', 'cmu_new2', 'cmu_new3', 'cmu_1006', '5yr_old', '8yr_old']:
        return 'z'
    elif parent_dir in ['sst', 'cmu', 'tcd', 'mixamo']:
        return 'y'
    else:
        assert False, "unrecognized parent directory for file: {}".format(filename)
