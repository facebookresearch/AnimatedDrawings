import numpy as np
import math
from numbers import Number
from PIL import Image, ImageOps
from string import Template
import os
import logging
from pathlib import Path
import cv2

from doctest import testmod

x_ax = np.array([1.0, 0.0, 0.0], np.float32)
y_ax = np.array([0.0, 1.0, 0.0], np.float32)
z_ax = np.array([0.0, 0.0, 1.0], np.float32)

###############################
global MOUSE_MODE
global MOUSE_MODE_VALUES
MOUSE_MODE_VALUES = ['MOVE_CAMERA', 'SELECTION']
MOUSE_MODE = 'MOVE_CAMERA'


def toggle_mouse_mode():
    global MOUSE_MODE
    MOUSE_MODE = MOUSE_MODE_VALUES[(MOUSE_MODE_VALUES.index(MOUSE_MODE) + 1) % len(MOUSE_MODE_VALUES)]
    print(MOUSE_MODE)


def get_mouse_mode():
    global MOUSE_MODE
    return MOUSE_MODE


###############################

###############################
global SHOW_ARAP_SKETCH
SHOW_ARAP_SKETCH = True


def toggle_arap_sketch_visibility():
    global SHOW_ARAP_SKETCH
    SHOW_ARAP_SKETCH = not SHOW_ARAP_SKETCH


def get_arap_sketch_visibility():
    global SHOW_ARAP_SKETCH
    return SHOW_ARAP_SKETCH


###############################

###############################
global SHOW_SKETCH_MESH
SHOW_SKETCH_MESH = False


def toggle_sketch_mesh_visibility():
    global SHOW_SKETCH_MESH
    SHOW_SKETCH_MESH = not SHOW_SKETCH_MESH


def get_sketch_mesh_visibility():
    global SHOW_SKETCH_MESH
    return SHOW_SKETCH_MESH


###############################

###############################
global SHOW_ARAP_HANDLES
SHOW_ARAP_HANDLES = False


def toggle_arap_handles_visibility():
    global SHOW_ARAP_HANDLES
    SHOW_ARAP_HANDLES = not SHOW_ARAP_HANDLES


def get_arap_handles_visibility():
    global SHOW_ARAP_HANDLES
    return SHOW_ARAP_HANDLES


###############################

###############################
global SHOW_SKETCH_SEGMENTS
SHOW_SKETCH_SEGMENTS = False


def toggle_sketch_segment_visibility():
    global SHOW_SKETCH_SEGMENTS
    SHOW_SKETCH_SEGMENTS = not SHOW_SKETCH_SEGMENTS


def get_sketch_segment_visibility():
    global SHOW_SKETCH_SEGMENTS
    return SHOW_SKETCH_SEGMENTS


###############################

###############################
global SHOW_MULTI_CAMERAS
SHOW_MULTI_CAMERAS = True


def toggle_camera_multi_view():
    global SHOW_MULTI_CAMERAS
    SHOW_MULTI_CAMERAS = not SHOW_MULTI_CAMERAS


def get_show_multi_cameras():
    global SHOW_MULTI_CAMERAS
    return SHOW_MULTI_CAMERAS

###############################

###############################
# an assortment of colors to use as needed
bone_colors = [
    (1.0, 0.0, 0.0),  # right side of character
    (0.5, 1.0, 0.5),  # right upper arm
    (0.0, 1.0, 0.0),  # right lower arm
    (1.0, 0.0, 0.0),  # left side of character
    (0.0, 0.0, 1.0),  # left upper arm
    (1.0, 1.0, 0.0),  # left lower arm
    (1.0, 0.0, 0.0),  # right hip torso area
    (0.0, 1.0, 1.0),  # right upper leg
    (0.5, 0.5, 1.0),  # right lower leg
    (1.0, 0.0, 0.0),  # left hip torso area
    (1.0, 0.5, 0.5),  # left upper leg
    (1.0, 0.0, 1.0),  # left lower leg
    (1.0, 0.0, 0.0),  # center of torso
    (1.0, 0.0, 0.0),  # head
]
colors = [
    (1.0, 1.0, 0.0),
    (1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 1.0, 1.0),
    (0.0, 0.0, 1.0),
    (1.0, 0.0, 1.0),
    (0.5, 0.5, 0.0),
    (0.5, 0.0, 0.0),
    (0.0, 0.5, 0.0),
    (0.0, 0.5, 0.0),
    (0.0, 0.5, 0.5),
    (0.0, 0.0, 0.5),
    (0.5, 1.0, 0.0),
    (0.0, 0.5, 1.0),
    (0.5, 0.0, 1.0),
    (1.0, 0.5, 0.0),
    (0.0, 1.0, 0.5),
    (1.0, 0.0, 0.5),
]
###############################

###############################
# segment names and order. Transferrer assumes a segment's parent appears before the segment in the ordering
segment_names = (
    'torso',
    'head',
    'left_arm_upper',
    'left_arm_lower',
    'right_arm_upper',
    'right_arm_lower',
    'left_leg_upper',
    'left_leg_lower',
    'right_leg_upper',
    'right_leg_lower',
)

###############################

###############################
global SHOW_SKETCH_SKELETON
SHOW_SKETCH_SKELETON = False


def toggle_sketch_skeleton_visibility():
    global SHOW_SKETCH_SKELETON
    SHOW_SKETCH_SKELETON = not SHOW_SKETCH_SKELETON


def get_sketch_skeleton_visibility():
    global SHOW_SKETCH_SKELETON
    return SHOW_SKETCH_SKELETON


###############################
# various meaningful groupings of bodyparts. Used by BVH cameras when
# they want to retarget motion onto a particular group of bodyparts
bodypart_groups = {
    'right_lower_limb_segments': [
        'right_leg_upper',
        'right_leg_lower'
    ],
    'left_lower_limb_segments': [
        'left_leg_upper',
        'left_leg_lower',
    ],
    'lower_limb_segments': [
        'left_leg_upper',
        'left_leg_lower',
        'right_leg_upper',
        'right_leg_lower'
    ],
    'upper_limb_segments': [
        'left_arm_upper',
        'left_arm_lower',
        'right_arm_upper',
        'right_arm_lower'
    ],
    'limb_segments': [
        'left_leg_upper',
        'left_leg_lower',
        'right_leg_upper',
        'right_leg_lower',
        'left_arm_upper',
        'left_arm_lower',
        'right_arm_upper',
        'right_arm_lower'
    ],
    'trunk_segments': [
        'torso',
        # 'head',
    ]
}
###############################
# used by Transferrer_Render.retarget()
cached_rot_name_to_index = {
    'fwd_vel': 0,
    'vrt_vel': 1,
    'left_arm_lower': 2,
    'left_arm_upper': 3,
    'left_leg_lower': 4,
    'left_leg_upper': 5,
    'right_arm_lower': 6,
    'right_arm_upper': 7,
    'right_leg_lower': 8,
    'right_leg_upper': 9,
    'torso': 10,
    'head' : 11
}
###############################

def identity():
    """ 4x4 identity matrix """
    return np.identity(4, 'f')


def view_matrix(self):
    """ View matrix transformation, including distance to target point """
    return translate(0, 0, 1) @ self.matrix()


def translate(x=0.0, y=0.0, z=0.0):
    """ matrix to translate from coordinates (x,y,z) or a vector x"""
    matrix = np.identity(4, 'f')
    matrix[:3, 3] = vec(x, y, z) if isinstance(x, Number) else vec(x)
    return matrix


def vec(*iterable):
    """ shortcut to make numpy vector of any iterable(tuple...) or vector """
    return np.asarray(iterable if len(iterable) > 1 else iterable[0], 'f')


def angle_from(v1, v2, degrees=True):
    """
    :param v1: starting vector
    :param v2: ending vector
    :return: CCW rotation about z angle in degrees from v1 to v2
    >>> angle_from(np.array([0, 1], np.float32), np.array([-1, 0], np.float32))
    90.0
    >>> angle_from(np.array([1, 0], np.float32), np.array([0,  1], np.float32))
    90.0
    >>> angle_from(np.array([1, 0], np.float32), np.array([0, -1], np.float32))
    270.0
    >>> angle_from(np.array([1, 0], np.float32), np.array([-1, 0], np.float32))
    180.0
    >>> angle_from(np.array([0, 0], np.float32), np.array([0,  0], np.float32))
    0.0
    """
    v1 = normalized(v1)
    v2 = normalized(v2)

    theta = math.atan2(v2[1], v2[0]) - math.atan2(v1[1], v1[0])
    if degrees:
        theta = math.degrees(theta)

    assert degrees is True

    theta = theta % 360.0
    if theta < 0.0:
        theta = theta + 360.0
    return theta


def angle_between(v1, v2, degrees=True):
    v1_n = normalized(v1)
    v2_n = normalized(v2)

    v1_length = np.linalg.norm(v1)
    v2_length = np.linalg.norm(v2)

    theta = math.acos(max(-1.0, min(1.0, np.dot(v1_n, v2_n))))

    if degrees is True:
        theta = math.degrees(theta)

    return theta


def matmul(a, b):
    """takes two nd.array matrices, checks they have correct row and col numbers, returns their product"""
    assert len(a.shape) == 2
    assert len(b.shape) == 2
    assert a.shape[0] == b.shape[1]

    return np.matmul(a, b)


def read_texture(filename, channels):
    import OpenGL.GL as GL
    logging.info(f'trying to open {filename}')
    try:
        if os.path.exists(filename):
            pass
        else:
            filename = '../Data/Texture/{}'.format(filename.split('/')[-1])
        image = Image.open(filename, 'r')

    except IOError as ex:
        logging.error('OPError: failed to open texture file')
        message = Template.template.format(type(ex).__name__, ex.args)
        logging.error(message)
        return -1
    logging.info(f'Opened file: size={image.size}, format={image.format}')
    image = ImageOps.flip(image)
    npimage = np.array(image)

    # make pixels outside mask transparent
    mask_p = Path(filename).parent / (str(Path(filename).stem) + '_mask.png')
    mask = cv2.imread(str(mask_p))[::-1,:,0]
    npimage[np.where(mask == 0)] = 0
    imageData = npimage.flatten()

    texture_id = GL.glGenTextures(1)
    GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 4)
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_BASE_LEVEL, 0)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAX_LEVEL, 0)
    GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, channels, image.size[0], image.size[1], 0, channels, GL.GL_UNSIGNED_BYTE,
                    imageData)

    image.close()
    return texture_id


# Linear Algebra operations
def normalized(vector):
    """ normalized version of any vector, with zero division check """
    norm = math.sqrt(sum(vector * vector))
    return vector / norm if norm > 0. else vector


def sincos(angle=0.0, radians=False):
    """ Rotation utility shortcut to compute sine and cosine of an angle. """
    if radians is False:
        angle = math.radians(angle)
    return math.sin(angle), math.cos(angle)


def translate(x=0.0, y=0.0, z=0.0):
    """ matrix to translate from coordinates (x,y,z) or a vector x"""
    matrix = np.identity(4, np.float32)
    matrix[0, 3] = x
    matrix[1, 3] = y
    matrix[2, 3] = z
    return matrix


def lookat(eye, target, up):
    """ Computes 4x4 view matrix from 3d point 'eye' to 'target',
        'up' 3d vector fixes orientation """
    view = normalized(vec(target)[:3] - vec(eye)[:3])
    up = normalized(vec(up)[:3])
    right = np.cross(view, up)
    up = np.cross(right, view)
    rotation = np.identity(4)
    rotation[:3, :3] = np.vstack([right, up, -view])
    return rotation @ translate(-eye)


def rotate(axis=(1.0, 0.0, 0.0), angle=0.0, radians=False):
    x, y, z = normalized(vec(axis))
    s, c = sincos(angle, radians)
    nc = 1 - c
    return np.array([[x * x * nc + c, x * y * nc - z * s, x * z * nc + y * s, 0],
                     [y * x * nc + z * s, y * y * nc + c, y * z * nc - x * s, 0],
                     [x * z * nc - y * s, y * z * nc + x * s, z * z * nc + c, 0],
                     [0, 0, 0, 1]], np.float32)


def scale(x, y=None, z=None):
    """scale matrix, with uniform (x alone) or per-dimension (x,y,z) factors"""
    x, y, z = (x, y, z) if isinstance(x, Number) else (x[0], x[1], x[2])
    y, z = (x, x) if y is None or z is None else (y, z)  # uniform scaling
    return np.diag((x, y, z, 1))


def constrain_angle(theta):
    while theta > 180.0:
        theta -= 360.0
    while theta < -180.0:
        theta += 180.0

    return theta


def point_in_triangle(pt, v1, v2, v3):
    """
    >>> point_in_triangle( [0, 0], [0.5, -0.5], [0.0, 0.5], [-0.5, -0.5])
    True
    >>> point_in_triangle( [1, 1], [0.5, -0.5], [0.0, 0.5], [-0.5, -0.5])
    False
    """

    def sign(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

    d1 = sign(pt, v1, v2)
    d2 = sign(pt, v2, v3)
    d3 = sign(pt, v3, v1)

    has_neg = d1 < 0 or d2 < 0 or d3 < 0
    has_pos = d1 > 0 or d2 > 0 or d3 > 0

    if not (has_neg and has_pos):
        return True
    else:
        return False


def squared_distance_between_point_and_line(x1, y1, x2, y2, x3, y3):  # x3, y3 is the point
    px = x2 - x1
    py = y2 - y1

    norm = px * px + py * py

    u = ((x3 - x1) * px + (y3 - y1) * py) / float(norm)

    if u > 1:
        u = 1
    elif u < 0:
        u = 0

    x = x1 + u * px
    y = y1 + u * py

    dx = x - x3
    dy = y - y3

    dist = (dx * dx + dy * dy)

    return dist


if __name__ == '__main__':
    testmod(name='util', verbose=True)
