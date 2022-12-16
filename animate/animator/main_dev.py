from animator.model.scene import Scene
from animator.model.camera import Camera
from animator.model.animated_drawing import AnimatedDrawing
from animator.model.transform import TransformWidget
from animator.controller.interactive_controller import InteractiveController
from animator.view.interactive_view import InteractiveView
from model.vectors import Vectors
from model.bvh import BVH
from model.quaternions import Quaternions
import logging
import yaml
import numpy as np

from model.arap import ARAP, old_ARAP

vertices = np.array([
    [0.0, 0.0],
    [1.0, 1.0],
    [2.0, 0.0]
    ])
triangles = np.array([
    [0, 1, 2]
],np.int32)

pin_v_idxs = np.array([0, 2])
new = ARAP(pin_v_idxs, triangles=triangles, vertices=vertices)
v2 = new.solve([[0, 0], [0, -4]])

assert np.isclose(v2, np.array([
    [0.00000000e+00, -2.99999100e-06],
    [1.00000000e+00, -2.00000000e+00],
    [6.93003543e-23, -3.99999700e+00]
    ])).all()

print('Passed!')




vertices = np.array([
    [1.0, 0.0],
    [1.0, 1.0],
    [2.0, 1.0],
    [2.0, 0.0],
    ])
triangles = np.array([
    [0, 1, 2],
    [0, 2, 3],
],np.int32)

pin_v_idxs = np.array([0, 3])

new = ARAP(np.empty(pin_v_idxs), triangles=triangles, vertices=vertices)
v2 = new.solve([[3, 0], [6, 0]])

assert np.isclose(v2, np.array([
    [0.00000000e+00, -2.99999100e-06],
    [1.00000000e+00, -2.00000000e+00],
    [6.93003543e-23, -3.99999700e+00]
    ])).all()

print('Passed!')

# old = old_ARAP(np.array([]), vertices=vertices, triangles=triangles)
# v2 = old._arap_solve([[0, 0], [0, -4]])
# y = 2
# def get_cfg():
#     with open('./config/base.yaml', 'r') as f:
#         base_cfg = yaml.load(f, Loader=yaml.FullLoader)
#         user_cfg = {}
#         return {**base_cfg, **user_cfg}  # scene_cfg is base overwitten by user
# 
# 
# if __name__ == '__main__':
#     logging.basicConfig(filename='log.txt', level=logging.DEBUG)
# 
#     cfg = get_cfg()
# 
#     scene = Scene(cfg)
# 
#     if True:  # code specific to running in 'interactive' mode
#         import glfw
#         glfw.init()
# 
#         view_camera = Camera(pos=Vectors([-0.5, -0.5, -3.0]), fwd=Vectors([0.0, 0.0, 1.0]))
#         scene.add_child(view_camera)
#         view = InteractiveView(cfg, view_camera)
# 
#         controller = InteractiveController(cfg, scene, view)
# 
#     # development code for animated drawing development
#     ad = AnimatedDrawing('tests/test_character/nick_cat.yaml')
#     q2 = Quaternions.from_euler_angles('z', np.array([-90]))
#     ad.rig.joints['right_elbow'].set_rotate(q2)
#     ad.rig._vertex_buffer_dirty_bit = True
#     ad.update_transforms()
#     scene.add_child(ad)
#     
#     p = ad.rig.get_joints_pos()
#     # ad.rig.set_position(np.array([-1, -2, -10]))
# 
#     controller.run()
