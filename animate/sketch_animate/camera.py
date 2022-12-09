import pyrr
from sketch_animate.util import *
from sketch_animate.Shapes.Box import Box
import numpy as np

# A list containing the type of objects that are visible in each camera type
camtype_visible_filter = {
    'free': ['BVH', 'Floor', 'Sketch', 'ARAP_Sketch', 'Drawing', 'Camera'],
    'sketch': ['Sketch', 'Floor', 'ARAP_Sketch'],
    'bvh': ['BVH', 'Floor'],
    'triangulation': ['Sketch', 'ARAP_Sketch', 'Floor']
}


class Camera:
    class Target:
        def __init__(self, joint_name: str):
            self.joint_name = joint_name
            self.model = np.identity(4, np.float32)
            self.pos = None
            self.yaw = 0.0
            self.fwd = np.zeros([3], np.float32)

        def set_position(self, x: float, y: float, z: float):
            """Set the world space target of the camera"""
            self.pos = [x, y, z]

        def set_forward(self, v: np.ndarray):
            self.fwd = v
            fwd = np.array([v[0], v[2]], np.float32)
            self.yaw = angle_from(x_ax, fwd)

        def get_transform(self):
            return translate(*self.pos) @ rotate(y_ax, -self.yaw)

    def __init__(self, cfg=None, pos=(0.0, 0.0, -1.0), up=(0.0, 1.0, 0.0), yaw=-90.0, pitch=0.0, speed=0.1,
                 sensitivity=0.1, name='no-name camera', cam_type=None):
        self.cfg = cfg
        self.pos = pos
        self.world_up = up
        self.yaw = yaw
        self.pitch = pitch
        self.speed = speed
        self.sensitivity = sensitivity

        assert cam_type in camtype_visible_filter.keys()
        self.cam_type = cam_type

        self.name = name

        self.target = None  # if we need the camera pointed and following a particular joint, use this. just a transform

        self.front = None
        self.right = None
        self.up = None
        self.update_camera_vectors()

        self.camera_widget = Box()
        self.update_widget()

    def initialize_target(self, joint_name: str):
        self.target = self.Target(joint_name)

    def initialize_pca_target(self, bvh, target_joints):
        self.centroids, self.pc3s = bvh.calculate_PCA_from_joint_list(target_joints)
        self.target = self.Target('pca_test')

    def set_target_position(self, pos: np.ndarray):
        self.target.set_position(*pos)

    def set_target_position_and_forward(self, pos: np.ndarray, fwd: np.ndarray):
        self.target.set_position(*pos)
        self.target.set_forward(fwd)
        self.update_widget()
        self.update_camera_vectors()

    def set_target_position_and_forward_from_frame(self, frame):
        pos = self.centroids[frame]
        fwd = self.pc3s[frame]

        self.target.set_position(*pos)
        self.target.set_forward(fwd)
        self.update_widget()
        self.update_camera_vectors()

    def get_global_position(self):
        return (self.target.get_transform() @ translate(*self.pos))[:-1, -1]

    def update_widget(self):
        model = np.linalg.inv(self.get_view_matrix()) @ scale(0.05, 0.05, 0.05)
        self.camera_widget.model = model

    def update_camera_vectors(self):
        front = np.empty([3], np.float32)
        front[0] = math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        front[1] = math.sin(math.radians(self.pitch))
        front[2] = math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        self.front = normalized(front)
        self.right = normalized(np.cross(self.front, self.world_up))
        self.up = normalized(np.cross(self.right, self.front))

    def set_from_pca_segmenter(self, target_pos, view_vector):
        # view_vector[1] = 0.0  # constrain to the equator

        self.pos = target_pos + 3 * normalized(view_vector)
        self.front = normalized(-view_vector)
        self.right = normalized(np.cross(self.front, self.world_up))
        self.up = normalized(np.cross(self.right, self.front))

        self.target.set_position(target_pos[0], target_pos[1], target_pos[2])

    def set_camera_pos_and_front_from_frame(self, frame):
        pos = self.centroids[frame]
        front = self.pc3s[frame]
        self.pos = pos + normalized(front)
        self.front = normalized(-front)
        self.right = normalized(np.cross(self.front, self.world_up))
        self.up = normalized(np.cross(self.right, self.front))

    def get_proj_matrix(self, width: int, height: int):
        proj = pyrr.matrix44.create_perspective_projection(35.0, width / height, 0.1, 100.0)
        return proj.T

    def get_view_matrix(self):
        # view = pyrr.matrix44.create_look_at(self.pos, self.pos + self.front, self.up).T
        view = pyrr.matrix44.create_look_at(self.pos, self.pos + self.front, self.up).T
        if self.target is not None:
            # view = pyrr.matrix44.create_look_at(self.pos, self.target.pos, self.up).T
            trans = self.target.get_transform()
            view = view @ np.linalg.inv(trans)

            # trans = translate(*self.target.pos)
            # view = view @ np.linalg.inv(trans)
            pass
        return view

    def process_keyboard(self, direction: str, deltaTime=1.0):
        velocity = self.speed * deltaTime
        if direction == 'forward':
            self.pos += self.front * velocity
        elif direction == 'backward':
            self.pos -= self.front * velocity
        elif direction == 'left':
            self.pos -= self.right * velocity
        elif direction == 'right':
            self.pos += self.right * velocity

        self.update_widget()

    def process_mouse_movement(self, xoffset: float, yoffset: float, constrain_pitch=True):
        xoffset *= self.sensitivity
        yoffset *= self.sensitivity
        self.yaw += xoffset
        self.pitch -= yoffset
        if constrain_pitch:
            if self.pitch > 89.0:
                self.pitch = 89.0
            if self.pitch < -89.0:
                self.pitch = -89.0

        self.update_camera_vectors()

        self.update_widget()

    def is_drawable_visible_in_camera(self, drawable):
        if type(drawable).__name__ not in camtype_visible_filter[self.cam_type]:
            return False

        if self.cam_type != 'bvh' and type(drawable).__name__ == 'BVH' and self.cfg['DRAW_BVH'] is False:
            return False

        if type(drawable).__name__ == 'Camera' and self.cfg['DRAW_CAMERA_WIDGETS'] is False:
            return False

        return True

    def draw(self, **kwargs):
        self.camera_widget.draw(**kwargs)
