import os
import os.path as osp
import sys

sys.path.append(osp.abspath(osp.dirname(__file__)))

import easydict
from vitpose.inference_pose import PoseEstimator

vitpose_root_path = osp.join(r'vitpose/easy_ViTPose')


def _check_and_add_add_absolute_path(cfg):
    pose2d_cfg_path = cfg.detector_2d.vit_pose.pose_config
    pose2d_model_path = cfg.detector_2d.vit_pose.pose_model
    detector_cfg_path = cfg.detector_2d.vit_pose.detector_config
    detector_model_path = cfg.detector_2d.vit_pose.detector_model

    if not osp.isabs(pose2d_cfg_path):
        pose2d_cfg_path = osp.join(osp.abspath(osp.dirname(__file__)), pose2d_cfg_path)
        cfg.detector_2d.vit_pose.pose_config = pose2d_cfg_path

    if not osp.isabs(pose2d_model_path):
        pose2d_model_path = osp.join(osp.abspath(osp.dirname(__file__)), pose2d_model_path)
        cfg.detector_2d.vit_pose.pose_model = pose2d_model_path

    if not osp.isabs(detector_cfg_path):
        detector_cfg_path = osp.join(osp.abspath(osp.dirname(__file__)), detector_cfg_path)
        cfg.detector_2d.vit_pose.detector_config = detector_cfg_path

    if not osp.isabs(detector_model_path):
        detector_model_path = osp.join(osp.abspath(osp.dirname(__file__)), detector_model_path)
        cfg.detector_2d.vit_pose.detector_model = detector_model_path


def inference_2d_keypoints_with_gen_npz(video_path, main_cfg):
    '''
    :param video_path: video source path
    :param main_cfg: from mian config file parameters
    :return:
        {
            kpts_2d: [T,V=17,C=2],
            kpts_score: [T,V=17,C=1],
        }
    '''
    # add absolute path
    _check_and_add_add_absolute_path(main_cfg)

    pose_estimator = PoseEstimator(from_main_cfg=main_cfg)
    ret_kpt_and_score = easydict.EasyDict({'kpt': None, 'score': None})
    pose_estimator.inference(ret_kpt_and_score=ret_kpt_and_score)
    kpts_2d, kpts_score = ret_kpt_and_score.kpt, ret_kpt_and_score.score
    if main_cfg.detector_2d.estimation_result.save_npz:
        import numpy as np
        save_npz_dir = osp.join('output_2dhpe_npz')
        os.makedirs(save_npz_dir, exist_ok=True)
        output_path_npz = osp.join(save_npz_dir, osp.basename(video_path).split('.')[0] + '_2dhpe.npz')
        print('>>> Keypoint2d and keypoint_2d npz save in ', output_path_npz)
        np.savez_compressed(output_path_npz, kpts=kpts_2d, kpts_score=kpts_score)
    return kpts_2d, kpts_score
