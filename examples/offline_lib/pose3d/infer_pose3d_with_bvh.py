import os
import os.path as osp
import sys

sys.path.append(osp.join(osp.abspath(osp.dirname(__file__))))
import torch
from torch.utils.data import DataLoader
import imageio
from tqdm import tqdm
import numpy as np

from .cfg.file_config import get_config

if torch.cuda.is_available():
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"  # see issue #152
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"


# combine parameters from cmd and yaml
# cmd > yaml
def combine_cfg_and_args():
    motion_config_file = osp.join(r'cfg/pose_config_with_bvh.yaml')
    cfg = get_config(motion_config_file)

    def get_args():
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('--vid_path', type=str, default='video/kunkun_cut.mp4', help='Wild video path.')
        args = parser.parse_args()
        return args

    def _check_and_add_absolute_path(cfg):
        pose3d_cfg_path = cfg.detector_3d.model_config_path
        pose3d_model_path = cfg.detector_3d.checkpoint_path

        if not osp.isabs(pose3d_cfg_path):
            pose3d_cfg_path = osp.join(osp.abspath(osp.dirname(__file__)), pose3d_cfg_path)

        if not osp.isabs(pose3d_model_path):
            pose3d_model_path = osp.join(osp.abspath(osp.dirname(__file__)), pose3d_model_path)

        cfg.detector_3d.model_config_path = pose3d_cfg_path
        cfg.detector_3d.checkpoint_path = pose3d_model_path

    args = get_args()
    cfg.video_path = args.vid_path
    _check_and_add_absolute_path(cfg)

    return cfg


# get video info
def get_vid_info(vid_path: str):
    vid = imageio.get_reader(vid_path, 'ffmpeg')
    fps_in = vid.get_meta_data()['fps']
    vid_size = vid.get_meta_data()['size']
    return vid, fps_in, vid_size


# get 2d keypoints from vitpose
def get_detector_2d(detector_name: str = 'vit_pose'):
    '''
    :param detector_name: str name of 2d dector's name (Currently, we only support 'vit_pos')
    :return:
    '''

    def get_vit_pose():
        from infer_pose2d import inference_2d_keypoints_with_gen_npz as vit_pose
        return vit_pose

    detector_map = {
        'vit_pose': get_vit_pose
    }

    assert detector_name in detector_map, f'2D detector: {detector_name} not implemented yet!'

    return detector_map[detector_name]()


# infer keypoints from trained model
def inference_pose3d(cfg, keypoints_2d: np.array, vid_w: int = None, vid_h: int = None, vid_fps: int = 25):
    '''

    :param cfg: config from *.yaml file
    :param keypoints_2d: [T,V,C=2+1]
    :param vid_w: frame width
    :param vid_h: frame height
    :param vid_fps: frame fps
    :return:
        prediction_camera_3d: [T,V,C]
    '''

    vid_size = (vid_w, vid_h)

    from .tool.dataset_wild import WildDetNumpyDataset
    from .tool.utils_data import flip_data
    import torch

    if cfg.detector_3d.checkpoint_path.endswith('.bin'):
        assert NotImplementedError, 'Currently, initial torch model is not supported!!'
    elif cfg.detector_3d.checkpoint_path.endswith('.onnx'):
        import onnxruntime
        print(">>> Supported onnxruntime version: ", onnxruntime.__version__)
        print(">>> Supported Opset versions: ", onnxruntime.get_available_providers())
        from .tool.model import PoseEstimator
        model_pos = PoseEstimator(from_main_cfg=cfg, model_path=cfg.detector_3d.checkpoint_path)
    else:
        assert NotImplementedError, 'Other formats of suffix checkpoint file for 3D pose are not supported now!!'

    testloader_params = {
        'batch_size': 1,
        'shuffle': False,
        'num_workers': 1,
        'pin_memory': True,
        'prefetch_factor': 4,
        'persistent_workers': True,
        'drop_last': False
    }
    if cfg.detector_3d.use_pixel_normalize:
        # Keep relative scale with pixel coornidates (we sue this branch currently)
        wild_dataset = WildDetNumpyDataset(numpy_data=keypoints_2d,
                                           clip_len=cfg.detector_3d.clip_len, vid_size=(vid_w, vid_h),
                                           scale_range=None,
                                           focus=None,
                                           format='coco')
    else:
        # Scale to [-1,1]
        wild_dataset = WildDetNumpyDataset(numpy_data=keypoints_2d, clip_len=cfg.detector_3d.clip_len,
                                           vid_size=None, scale_range=[1, 1], focus=None, format='coco')

    test_loader = DataLoader(wild_dataset, **testloader_params)
    results_all = []
    with torch.no_grad():
        for batch_input in tqdm(test_loader):
            N, T = batch_input.shape[:2]
            if torch.cuda.is_available():
                batch_input = batch_input.cuda()

            if cfg.detector_3d.no_conf:
                batch_input = batch_input[:, :, :, :2]

            if cfg.detector_3d.flip_augument:
                # flip data for argument (we use this branch currently)
                batch_input_flip = flip_data(batch_input)
                predicted_3d_pos_1 = model_pos(batch_input)
                predicted_3d_pos_flip = model_pos(batch_input_flip)
                predicted_3d_pos_2 = flip_data(predicted_3d_pos_flip)  # Flip back
                predicted_3d_pos = (predicted_3d_pos_1 + predicted_3d_pos_2) / 2.0
            else:
                predicted_3d_pos = model_pos(batch_input)

            if cfg.detector_3d.rootrel:
                # In this mode, the root joint is all around 0
                predicted_3d_pos[:, :, 0, :] = 0  # [N,T,17,3]
            else:
                # In this mode, the start time's z-axith is 0
                # we use this branch currently
                predicted_3d_pos[:, 0, 0, 2] = 0
                pass

            # not used currently
            if cfg.detector_3d.gt_2d:
                predicted_3d_pos[..., :2] = batch_input[..., :2]

            if isinstance(predicted_3d_pos, torch.Tensor):
                predicted_3d_pos = predicted_3d_pos.cpu().numpy()
            results_all.append(predicted_3d_pos)

    results_all = np.hstack(results_all)
    results_all = np.concatenate(results_all)
    results_all = results_all[:wild_dataset.total_frame()]

    # if visualize, its range will in [-1,1] if needed
    if cfg.detector_3d.estimation_result.export_mp4:
        print(f'>>> Export video result saving...')
        from .tool.vismo import render_and_save
        save_path = osp.join('output_3dhpe', osp.basename(cfg.video_path).split('.')[0] + '_3dhpe.mp4')
        render_and_save(results_all, save_path=save_path, keep_imgs=True, fps=vid_fps)
        print(f'>>> Sucessfully save video path in {save_path}')

        if cfg.detector_3d.estimation_result.export_gif:
            print(f'>>> Export gif result saving...')
            from .tool.vismo import convert_video2gif
            convert_video2gif(save_path)
            print(f'>>> Sucessfully save video path in {save_path}')

    # convert to pixel corrdinate,corresponding range is [0,H] and [0,W] respectively
    if cfg.detector_3d.use_pixel_restore:
        results_all = results_all * (min(vid_size) / 2.0)
        results_all[:, :, :2] = results_all[:, :, :2] + np.array(vid_size) / 2.0

    prediction_camera_3d = results_all
    return prediction_camera_3d


# generate bvh file
def generate_bvh(cfg, camera_keypoints_3d):
    '''

    :param cfg: config from *.yaml file
    :param camera_keypoints_3d: [T,V,C], in camera space
    :return: str, bvh file path
    '''
    print('>> Generating bvh file...')
    bvh_cfg = cfg.bvh

    from .tool.camera import camera_to_world
    world_keypoints_3d = camera_to_world(camera_keypoints_3d,
                                         R=np.array(bvh_cfg.camera.extrinsics.R, dtype=np.float32),
                                         t=0)

    world_keypoints_3d_smartbody = np.zeros_like(world_keypoints_3d)

    # transfer to smartbody format +Y up and +X right
    X = world_keypoints_3d[..., 0] * bvh_cfg.scale_factor
    Y = world_keypoints_3d[..., 1] * bvh_cfg.scale_factor
    Z = world_keypoints_3d[..., 2] * bvh_cfg.scale_factor

    world_keypoints_3d_smartbody[..., 0] = -X
    world_keypoints_3d_smartbody[..., 1] = Z
    world_keypoints_3d_smartbody[..., 2] = Y

    from .tool.bvh.generator.smartbody_skeleton import SmartBodySkeleton

    output_dir_bvh = 'output_3dhpe_bvh'
    os.makedirs(output_dir_bvh, exist_ok=True)
    video_name = osp.basename(cfg.video_path).split('.')[0]
    save_path = osp.join(output_dir_bvh, video_name + '_smartbody.bvh')

    smartbody_skeleton = SmartBodySkeleton()
    smartbody_skeleton.poses2bvh(world_keypoints_3d_smartbody, output_file=save_path)

    print(f'>>> Sucessfully save *.bvh file in {save_path}')
    return save_path


# get 2d results and 3d results
def main(cfg, vid_size, vid_fps):
    vid_w, vid_h = vid_size

    # 1.acquire 2d detectors
    detector_2d = get_detector_2d(cfg.detector_2d.selected_name)

    # acquire 2d keypoints from 2d keypoint detectors directly or from npz file
    if cfg.detector_2d.input_npz == '':
        video_path = cfg.video_path
        video_name = osp.basename(video_path).split('.')[0]
        # [T,V,2] and [T,V,1]  C=2+1 , here x and y is not normalized!!
        keypoints_2d, keypoints_2d_score = detector_2d(video_path, cfg)
    else:
        # assert NotImplementedError, 'Currently, directly read 2d kyepoints from npz file is not supported!!'
        keypoints_tuple = np.load(cfg.detector_2d.input_npz, allow_pickle=True)
        keypoints_2d, keypoints_2d_score = keypoints_tuple['kpts'], keypoints_tuple['kpts_score']

    print('>> Successfully predicted 2D keypoints!!')

    # 2.  2d -> 3d keypoint lifting
    keypoints_2d_combine = np.concatenate([keypoints_2d, keypoints_2d_score], axis=-1)
    prediction_camera_3d = inference_pose3d(cfg=cfg, keypoints_2d=keypoints_2d_combine,
                                            vid_w=vid_w, vid_h=vid_h, vid_fps=vid_fps)
    print('>> Successfully predicted 3D keypoints!!')

    # 3. generate bvh file
    bvh_path = generate_bvh(cfg, prediction_camera_3d)
    print(f'>>> Sucessfully saved *.bvh file')

    return bvh_path


if __name__ == '__main__':
    # load config from certain *.yaml config file and cmd
    cfg = combine_cfg_and_args()
    video_file_path = cfg.video_path
    _, vid_fps, vid_size = get_vid_info(video_file_path)
    main(cfg, vid_size, vid_fps)
