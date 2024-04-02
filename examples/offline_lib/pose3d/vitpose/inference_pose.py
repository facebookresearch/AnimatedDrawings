import os
import os.path as osp
import sys

import easydict

sys.path.append(osp.abspath(osp.dirname(__file__)))

import time
import numpy as np
import numpy.typing as npt
from PIL import Image

from easy_ViTPose.vit_utils.visualization import joints_dict
import cv2
from easy_ViTPose import VitInferenceHuman
from config.file_config import get_config
from typing import Any, Dict, Union, Tuple, List
import torch

import tqdm
import json
from copy import deepcopy


# load and combine config parameter
def get_args(cur_cfg_path: str, from_main_cfg=None):
    # load current project configs
    cfg = get_config(cur_cfg_path)
    # if main config is not None, then we should combine
    if from_main_cfg is not None:
        def _combine_from_main_cfg():
            cfg.yolo.path = from_main_cfg.detector_2d.vit_pose.detector_model
            cfg.vit_pose.path = from_main_cfg.detector_2d.vit_pose.pose_model
            # combine main path into current configs
            cfg.input = from_main_cfg.video_path
            cfg.output.dir = from_main_cfg.detector_2d.vit_pose.output_dir

        _combine_from_main_cfg()

    # combine current configs <- parent configs
    cfg.use_mps = hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()
    cfg.use_cuda = torch.cuda.is_available()

    return cfg


dataset_and_joint_num_dict = {
    'coco': 17,
    'coco_25': 25,
    'wholebody': 133,
    'mpii': 16,
    'ap10k': 17,
    'apt36k': 17,
    'aic': 13
}


class PoseEstimator():
    def __init__(self, yaml_path: str = None, from_main_cfg=None):
        if yaml_path is not None:
            self.yaml_path = yaml_path
        else:
            self.yaml_path = from_main_cfg.detector_2d.vit_pose.pose_config
        self.cfg = get_args(self.yaml_path, from_main_cfg)
        self.pose_model_name = self.cfg.pose_model_name
        self.detect_model_name = self.cfg.detector_model_name

        self.joint_num = dataset_and_joint_num_dict[self.cfg.vit_pose.dataset]

    def inference(self, ret_kpt_and_score: easydict.EasyDict):
        '''
        Note: The predictions of 2D pose estimation from the Easy_VitPose library are in reverse order compared to to others,
        which is in the format of (y, x, score).
        Therefore, it requires manipulation to reverse (y, x, score) to (x, y, score) format.
        Inference on video, image, or camera device data."
        :param ret_kpt_and_score: EasyDict，which contains two key : 'kpt' and 'score', their corresponding shape are [T,V,C=2] and [T,V,C=1] respectively.
        :return:
        '''
        assert not (
                self.cfg.output.save_img or self.cfg.output.save_json or self.cfg.output.save_npz) or self.cfg.output.dir, \
            'Specify an output path if using save-img or save-json flags'
        input_path = self.cfg.input
        ext = input_path[input_path.rfind('.'):]
        output_path = self.cfg.output.dir
        if output_path:
            # If save json,image,and npz file
            if os.path.isdir(output_path):
                output_path = osp.join(output_path, f"{self.pose_model_name}_{osp.basename(input_path).split('.')[0]}")
                os.makedirs(output_path, exist_ok=True)
                save_name_img = os.path.basename(input_path).replace(ext, f"_result{ext}")
                save_name_json = 'vitpose-results.json'
                save_name_npz = os.path.basename(input_path).replace(ext, ".npz")

                output_path_img = os.path.join(output_path, save_name_img)
                output_path_json = os.path.join(output_path, save_name_json)
                output_path_npz = os.path.join(output_path, save_name_npz)
            # This branch is not used currently!!
            else:
                output_path_img = output_path + f'{ext}'
                output_path_json = output_path + '.json'
                output_path_npz = output_path + '.npz'

        # Load the image / video reader
        try:  # Check if is webcam
            int(input_path)
            is_video = True
            # Get file name without suffix.
            file_name = osp.basename(input_path).split('.')[0]
        except ValueError:
            from .support_video_suffix import VIDEO_SUFFIX_LIST
            assert os.path.isfile(input_path), 'The input file does not exist'
            is_video = input_path[input_path.rfind('.') + 1:].lower() in VIDEO_SUFFIX_LIST

        wait = 0
        total_frames = 1
        if is_video:
            from easy_ViTPose.vit_utils.inference import VideoReader
            reader = VideoReader(input_path, self.cfg.vit_pose.rotate)
            cap = cv2.VideoCapture(input_path)  # type: ignore
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            wait = 15
            if self.cfg.output.save_img:
                cap = cv2.VideoCapture(input_path)  # type: ignore
                fps = cap.get(cv2.CAP_PROP_FPS)
                ret, frame = cap.read()
                cap.release()
                assert ret
                assert fps > 0
                output_size = frame.shape[:2][::-1]
                out_writer = cv2.VideoWriter(output_path_img,
                                             cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
                                             fps, output_size)  # type: ignore
        else:
            reader = [np.array(Image.open(input_path).rotate(self.cfg.vit_pose.rotate))]  # type: ignore

        # Initialize model
        self.model = VitInferenceHuman(self.cfg.vit_pose.path, self.cfg.yolo.path, self.cfg.vit_pose.model_type,
                                       self.cfg.yolo.det_class, self.cfg.vit_pose.dataset,
                                       self.cfg.yolo.size, is_video=is_video,
                                       single_pose=self.cfg.vit_pose.single_pose,
                                       yolo_step=self.cfg.yolo.step)  # type: ignore
        print(f">>> Pose Model loaded: {self.cfg.vit_pose.path}")
        print(f'>>> Running inference on {input_path}')

        keypoints: List[Dict[Any, Any]] = []
        bboxes: List[npt.NDArray[np.float32]] = []  # each element in x1y1x2y2 format
        fps = []
        tot_time = 0.

        for (ith, img) in tqdm.tqdm(enumerate(reader), total=total_frames):
            t0 = time.time()

            # Run inference
            frame_keypoints, bbox = self.model.inference(img)
            bboxes.append(bbox)
            keypoints.append(frame_keypoints)

            delta = time.time() - t0
            tot_time += delta
            fps.append(delta)

            # Draw the poses and save the output img
            if self.cfg.output.show or self.cfg.output.save_img:
                # Draw result and transform to BGR
                img = self.model.draw(self.cfg.output.yolo_show, self.cfg.output.yolo_show_raw,
                                      self.cfg.vit_pose.conf_threshold)[..., ::-1]

                if self.cfg.output.save_img:
                    # TODO: If exists add (1), (2), ...
                    if is_video:
                        out_writer.write(img)
                    else:
                        print('>>> Saving output image')
                        cv2.imwrite(output_path_img, img)

                if self.cfg.output.show:
                    cv2.imshow('preview', img)
                    cv2.waitKey(wait)

        if is_video:
            tot_poses = sum(len(k) for k in keypoints)
            print(f'>>> Mean inference FPS: {1 / np.mean(fps):.2f}')
            print(f'>>> Total poses predicted: {tot_poses} mean per frame: '
                  f'{(tot_poses / (ith + 1)):.2f}')
            print(f'>>> Mean FPS per pose: {(tot_poses / tot_time):.2f}')

        if is_video and self.cfg.output.save_img:
            out_writer.release()
        cv2.destroyAllWindows()

        person_cnt = np.max([len(item) for item in keypoints]).item()
        ####################################################################
        # Saving operation
        # save json (not used currently)
        if self.cfg.output.save_json:
            print('>>> Saving output json')
            from easy_ViTPose.vit_utils.inference import NumpyEncoder
            with open(output_path_json, 'w') as f:
                out = {'keypoints': keypoints,
                       'skeleton': joints_dict()[self.model.dataset]['keypoints']}
                json.dump(out, f, cls=NumpyEncoder)

        # Save only first person or person with custom tracker
        if self.cfg.vit_pose.single_pose and person_cnt > 1:
            print('>>> Warning: There have two or more people, we choose the first person to save result.')
        elif person_cnt > 1:
            print('>>> Warning: There have two or more people, we choose the first person to save result.')

        kpts_2d = None
        kpts_score = None
        for kpts_and_score in keypoints:
            # current frame has no person
            if len(kpts_and_score.keys()) == 0:
                continue
            # tracker for correct tracker id
            if self.cfg.vit_pose.tracker_id not in kpts_and_score.keys():
                tracker_key = next(iter(kpts_and_score))
            else:
                tracker_key = self.cfg.vit_pose.tracker_id

            # [V,C] -> [T=1,V,C]
            kpts_and_score = np.array(kpts_and_score[tracker_key], dtype=np.float32)
            kpts_and_score = np.expand_dims(kpts_and_score, axis=0)
            if kpts_2d is None:
                # (y,x) -> (x,y)
                kpts_2d = deepcopy(kpts_and_score[..., [1, 0]])
                # (score)
                kpts_score = deepcopy(kpts_and_score[..., 2:])
            else:
                # (y,x) -> (x,y)
                kpts_2d = np.concatenate([kpts_2d, kpts_and_score[..., [1, 0]]], axis=0)
                # (score)
                kpts_score = np.concatenate([kpts_score, kpts_and_score[..., 2:]], axis=0)

        ret_kpt_and_score.kpt, ret_kpt_and_score.score = kpts_2d, kpts_score
        # save npz file
        if self.cfg.output.save_npz:
            print('>>> Saving output npz')
            print('>>> Keypoint2d and keypoint_2d npz save in ', output_path_npz)
            np.savez_compressed(output_path_npz, kpts=kpts_2d, kpts_score=kpts_score)


# Simpler test demo
def test_simpler():
    # Image to run inference RGB format
    img = cv2.imread('./example/test1.jpeg')
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # set is_video=True to enable tracking in video inference
    # be sure to use VitInference.reset() function to reset the tracker after each video
    # There are a few flags that allows to customize VitInference, be sure to check the class definition
    model_path = r'./checkpoints/vitpose-b-coco.onnx'
    yolo_path = r'checkpoints/yolov8/yolov8s.pt'

    # If you want to use MPS (on new macbooks) use the torch checkpoints for both ViTPose and Yolo
    # If device is None will try to use cuda -> mps -> cpu (otherwise specify 'cpu', 'mps' or 'cuda')
    # dataset and det_class parameters can be inferred from the ckpt name, but you can specify them.
    model = VitInferenceHuman(model_path, yolo_path, model_name='s', yolo_size=320, is_video=False, device=None)

    # Infer keypoints, output is a dict where keys are person ids and values are keypoints (np.ndarray (25, 3): (y, x, score))
    # If is_video=True the IDs will be consistent among the ordered video frames.
    keypoints = model.inference(img)

    # call model.reset() after each video

    img = model.draw(show_yolo=True)  # Returns RGB image with drawings
    cv2.imshow('image', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    cv2.waitKey(0)


if __name__ == '__main__':
    yaml_path = osp.join('config', 'default_config.yaml')
    test_loader = PoseEstimator(yaml_path=yaml_path)
    ret_kpt_and_score = easydict.EasyDict({'kpt': None, 'score': None})
    test_loader.inference(ret_kpt_and_score)
