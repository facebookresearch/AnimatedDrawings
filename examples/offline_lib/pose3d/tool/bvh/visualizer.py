import os
import os.path as osp
import sys

sys.path.append(osp.join(osp.dirname(__file__)))

import numpy as np
import numpy.typing as npt
import cv2
from deparser.joint import Joint
from deparser.bvh import BVH
from deparser.vectors import Vectors
from deparser.transform import Transform
from typing import List, Dict, Tuple, Union
from copy import deepcopy
from scipy.spatial.transform import Rotation


# simple visualizer for bvh
class BVHVisualizer():
    def __init__(self, bvh_path: str):
        self.bvh_path = bvh_path
        self.bvh = BVH.from_file(osp.join(bvh_path), init_root_rot_eular=(0.0, 0.0, 0.0))
        self.bvh_name = self.bvh.name


        self.all_joint_names: List[str] = self.bvh.get_joint_names()
        self.joint_num: int = self.bvh.joint_num
        self.root_joint = self.bvh.root_joint

        self.chain_joint_names_from_root: List[List[str]] = self.bvh.chain_joint_names_fron_root
        self.chain_joint_names_to_idx_dict: List[Dict[str, int]] = self.bvh.chain_joint_names_to_idx_dict_from_root

        self.total_frame = self.bvh.frame_max_num
        self.fps: float = self.bvh.frame_time * 1000

    def visualize_animated_orthogonal_projection(self,
                                                 canvas_w: int, canvas_h: int,
                                                 offset_x: int, offset_y: int,
                                                 scale: float):
        '''
        Visualize in 2D canvas with simple removed z axis
        :param canvas_w: canvas width
        :param canvas_h: canvas height
        :param offset_x: x offset
        :param offset_y: y offset
        :param scale: scale factor
        :return:
        '''
        self.canvas_w = canvas_w
        self.canvas_h = canvas_h

        self.bvh.apply_frame(frame_num=0)
        start_root_pos: Vectors = self.root_joint.get_world_position()
        self.bvh.offset(-start_root_pos)
        self.bvh.set_scale(scale=scale)

        delay = self._get_delay_from_fps(fps=self.fps)

        for t in range(self.total_frame):
            blank_canvas = self._create_blank_canvas(w=canvas_w, h=canvas_h)

            self.bvh.apply_frame(frame_num=t)

            # [V*C=3], and add relative offset
            all_frame_data: npt.NDArray[np.float32] = self.root_joint.get_chain_worldspace_positions()
            all_frame_data += np.tile(np.array([offset_x, offset_y, 0.0], dtype=np.float32), reps=(self.joint_num))

            # draw point
            # here, we simply remove z
            joint_x, joint_y = all_frame_data[0::3], all_frame_data[1::3]
            for x, y in zip(joint_x, joint_y):
                # 因为画板二维平面的y轴方向和实际坐标系的方向相反，这里要先做取反y轴的方向
                cv2.circle(blank_canvas, (int(x), int(canvas_h - y)), radius=3, color=(0, 0, 255), thickness=-1)

            # draw line
            for chain_idx, cur_sequence in enumerate(self.chain_joint_names_from_root):
                for idx in range(1, len(cur_sequence)):
                    # acquire start name and end name
                    start_name = cur_sequence[idx - 1]
                    end_name = cur_sequence[idx]
                    # acquire start index and end index
                    start_idx = self.chain_joint_names_to_idx_dict[chain_idx][start_name]
                    end_idx = self.chain_joint_names_to_idx_dict[chain_idx][end_name]

                    # draw line with opencv
                    cv2.line(blank_canvas, pt1=(int(joint_x[start_idx]), int(canvas_h - joint_y[start_idx])),
                             pt2=(int(joint_x[end_idx]), int(canvas_h - joint_y[end_idx])),
                             color=(255, 0, 0), thickness=2)

            # show canvas
            cv2.imshow('res', blank_canvas)
            cv2.waitKey(delay)

    # create empty canvas
    def _create_blank_canvas(self, w: int, h: int):
        return np.ones((h, w, 3), dtype=np.uint8) * 255

    # caculate delay from fps
    def _get_delay_from_fps(self, fps: float):
        return int(1000 / fps)

    def visualize_init_pose_orthogonal_projection(self, canvas_w: int, canvas_h: int,
                                                  offset_x: int, offset_y: int,
                                                  scale: float):
        '''
        简单的正交投影来实现初始姿态的二维可视化
        :param canvas_w: canvas width
        :param canvas_h: canvas height
        :param offset_x: x offset
        :param offset_y: y offset
        :param scale: scale factor
        :return:
        '''
        self.bvh.apply_frame(frame_num=-1)  # self.bvh.apply_init_local_offset()
        self.bvh.set_scale(scale=scale)
        start_root_pos: Vectors = self.root_joint.get_world_position()
        self.bvh.offset(-start_root_pos)

        init_frame_data: npt.NDArray[np.float32] = np.array(self.root_joint.get_chain_worldspace_positions())
        init_frame_data += np.tile(np.array([offset_x, offset_y, 0.0], dtype=np.float32), reps=(self.joint_num))

        blank_canvas = self._create_blank_canvas(w=canvas_w, h=canvas_h)

        # draw point
        # draw with directly removed z-axith
        joint_x, joint_y = init_frame_data[0::3], init_frame_data[1::3]
        for x, y in zip(joint_x, joint_y):
            cv2.circle(blank_canvas, (int(x), int(canvas_h - y)), radius=3, color=(0, 0, 255), thickness=-1)

        # draw line
        for chain_idx, cur_sequence in enumerate(self.chain_joint_names_from_root):
            for idx in range(1, len(cur_sequence)):
                start_name = cur_sequence[idx - 1]
                end_name = cur_sequence[idx]

                start_idx = self.chain_joint_names_to_idx_dict[chain_idx][start_name]
                end_idx = self.chain_joint_names_to_idx_dict[chain_idx][end_name]

                cv2.line(blank_canvas, pt1=(int(joint_x[start_idx]), int(canvas_h - joint_y[start_idx])),
                         pt2=(int(joint_x[end_idx]), int(canvas_h - joint_y[end_idx])),
                         color=(255, 0, 0), thickness=2)

        # show canvas
        cv2.imshow('res', blank_canvas)
        cv2.waitKey(-1)


if __name__ == '__main__':
    bvh_path = osp.join(
        osp.join(r"demo.bvh"))
    visualizer = BVHVisualizer(bvh_path=bvh_path)

    # get all animated pose
    visualizer.visualize_animated_orthogonal_projection(canvas_w=600, canvas_h=600, offset_x=120, offset_y=100,
                                                        scale=2.0)

    # get init pose
    visualizer.visualize_init_pose_orthogonal_projection(canvas_w=600, canvas_h=600, offset_x=200, offset_y=200,
                                                         scale=2.0)
