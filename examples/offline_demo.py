import os
import os.path as osp
import sys
import shutil

import yaml

sys.path.append(osp.dirname(osp.abspath(__file__)))

from animated_drawings import render
import os.path as osp
from offline_lib.sketch.sketch_estimator_and_detector import SketchDetectorAndEstimator
from offline_lib.tool.config import convert_easydict_to_dict

img_suffix = 'png'
script_source_path = osp.abspath(osp.dirname(__file__))
tmp_dir = osp.join(script_source_path, 'tmp')


# combine parameters from cmd and yaml
# cmd > yaml
def combine_cfg_and_args():
    from offline_lib.tool.config import get_config
    main_config_file = osp.join(script_source_path, r'offline_lib/mvc/video_base.yaml')
    cfg = get_config(main_config_file)

    def get_args():
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('--src_sketch', type=str, default='input/texture.png', help='The source sketch image path.')
        parser.add_argument('--src_motion', type=str, default='offline_lib/bvh/clapping_hand_smartbody.bvh',
                            help='The motion source file path that can be wild video or generated bvh that is human3.6m 17keypoints format.')
        parser.add_argument('--out_vid', type=str, default='./video.mp4', help='Custom output video path.')
        args = parser.parse_args()
        return args

    args = get_args()
    cfg.motion.input_file_path = args.src_motion
    cfg.sketch.image_path = args.src_sketch
    cfg.controller.OUTPUT_VIDEO_PATH = args.out_vid
    return cfg


def reload_config_files(main_cfg=None):
    from offline_lib.tool.config import get_config
    if main_cfg is None:
        main_cfg = get_config('offline_lib/mvc/video_base.yaml')

    other_cfgs = main_cfg.scene.ANIMATED_CHARACTERS[0]

    character_cfg = get_config(other_cfgs.character_cfg)
    motion_cfg = get_config(other_cfgs.motion_cfg)
    retarget_cfg = get_config(other_cfgs.retarget_cfg)
    sketch_image_path, sketch_cfg = main_cfg.sketch.image_path, main_cfg.sketch.model
    input_motion_path, pose3d_cfg = main_cfg.motion.input_file_path, main_cfg.motion.pose3d

    # 1. first, we should use detector and estimator to get
    sketch_detector_and_estimator(main_cfg, sketch_cfg, sketch_image_path)

    # 2. select correct motion from *.bvh file or video
    motion_info_acquire(main_cfg, motion_cfg, input_file_path=input_motion_path, pose3d_cfg=pose3d_cfg)

    # # 3. regenrate relative config file
    main_cfg_path = regenerate_config(main_cfg, character_cfg, motion_cfg, retarget_cfg)
    return main_cfg_path


def sketch_detector_and_estimator(main_cfg, sketch_cfg, img_path: str):
    print('>>> Sketch detector and estimation start')
    input_dir, img_suffix = osp.dirname(img_path), osp.basename(img_path).split('.')[-1]

    sketch_executor = SketchDetectorAndEstimator(
        detector_path=sketch_cfg.detector_path,
        estimator_path=sketch_cfg.estimator_path
    )
    sketch_executor.inference(img_path, show_res=sketch_cfg.show_intermidate_result,
                              need_mask=True,
                              morphops_iteration=sketch_cfg.mor_ite, out_dir=input_dir)

    main_cfg.scene.ANIMATED_CHARACTERS[0].character_cfg = sketch_executor.char_cfg_path


def motion_info_acquire(main_cfg, motion_cfg, input_file_path, pose3d_cfg=None):
    print('>>> Motion information acquire')
    VIDEO_SUFFIX_LIST = ['mp4', 'mov', 'avi']
    motion_file_suffix = osp.basename(input_file_path).split('.')[-1]
    if motion_file_suffix in VIDEO_SUFFIX_LIST:
        print('>>> Acquire Motion from video')

        def _check_and_add_absolute_path(cfg):
            pose3d_cfg_path = cfg.detector_3d.model_config_path
            pose3d_model_path = cfg.detector_3d.checkpoint_path

            if not osp.isabs(pose3d_cfg_path):
                pose3d_cfg_path = osp.join(osp.abspath(osp.dirname(__file__)), 'offline_lib', 'pose3d', pose3d_cfg_path)

            if not osp.isabs(pose3d_model_path):
                pose3d_model_path = osp.join(osp.abspath(osp.dirname(__file__)), 'offline_lib', 'pose3d',
                                             pose3d_model_path)

            cfg.detector_3d.model_config_path = pose3d_cfg_path
            cfg.detector_3d.checkpoint_path = pose3d_model_path

        from offline_lib.tool.config import get_config
        from offline_lib.pose3d.infer_pose3d_with_bvh import get_vid_info
        from offline_lib.pose3d.infer_pose3d_with_bvh import main as video_infer_main

        video_motion_config_file = main_cfg.motion.pose3d.cfg
        video_motion_cfg = get_config(video_motion_config_file)
        _check_and_add_absolute_path(cfg=video_motion_cfg)
        video_motion_cfg.video_path = input_file_path
        _, vid_fps, vid_size = get_vid_info(input_file_path)
        bvh_path = video_infer_main(video_motion_cfg, vid_size, vid_fps)
        input_file_path = bvh_path

    # This branch is dealt with final result
    elif motion_file_suffix == 'bvh':
        print('>>> Acquire Motion from bvh')
        pass
    else:
        assert NotImplementedError, 'Currently, other motion file format is not supported!!'

    # dealing final result with *.bvh
    from offline_lib.pose3d.tool.bvh.deparser.bvh import BVH
    bvh_cfg = BVH.from_file(input_file_path)
    frame_num, fps = bvh_cfg.frame_max_num, bvh_cfg.frame_time * 1000
    motion_cfg.filepath = input_file_path
    motion_cfg.start_frame_idx, motion_cfg.end_frame_idx = 0, frame_num - 1

    print('>>> Bind bvh successfully!!')


def regenerate_config(main_cfg, character_cfg, motion_cfg, retarget_cfg):
    os.makedirs(tmp_dir, exist_ok=True)
    # for character config, it relies on *.yaml, mask and texture currently
    character_cfg_path = main_cfg.scene.ANIMATED_CHARACTERS[0].character_cfg

    character_cfg_file_name = osp.basename(character_cfg_path)
    character_cfg_dir = osp.dirname(character_cfg_path)
    character_cfg_dir_relative = character_cfg_dir.split(osp.sep)[-1]

    target_character_cfg_dir = osp.join(tmp_dir, character_cfg_dir_relative)
    target_character_cfg_path = osp.join(tmp_dir, character_cfg_dir, character_cfg_file_name)

    if osp.exists(target_character_cfg_dir):
        shutil.rmtree(target_character_cfg_dir)

    shutil.copytree(character_cfg_dir, target_character_cfg_dir)
    texture_image_path = osp.join(target_character_cfg_dir, f'cropped_image.{img_suffix}')
    mask_image_path = osp.join(target_character_cfg_dir, f'mask_image.{img_suffix}')
    os.rename(texture_image_path, osp.join(osp.dirname(texture_image_path), f'texture.{img_suffix}'))
    os.rename(mask_image_path, osp.join(osp.dirname(mask_image_path), f'mask.{img_suffix}'))
    os.rename(target_character_cfg_path, osp.join(target_character_cfg_dir, 'char_cfg.yaml'))

    main_cfg.scene.ANIMATED_CHARACTERS[0].character_cfg = osp.join(target_character_cfg_dir, 'char_cfg.yaml')

    # for motion config, it relies on bvh config file
    target_motion_cfg_path = osp.join(tmp_dir, 'motion_cfg.yaml')
    with open(target_motion_cfg_path, 'w') as f:
        yaml.dump(convert_easydict_to_dict(motion_cfg), f)
    main_cfg.scene.ANIMATED_CHARACTERS[0].motion_cfg = target_motion_cfg_path

    # for retarget config ,currently, we only copy directly
    target_retarget_cfg_path = osp.join(tmp_dir, 'retarget_cfg.yaml')
    shutil.copy(main_cfg.scene.ANIMATED_CHARACTERS[0].retarget_cfg, target_retarget_cfg_path)
    main_cfg.scene.ANIMATED_CHARACTERS[0].retarget_cfg = target_retarget_cfg_path

    main_cfg.scene.ANIMATED_CHARACTERS[0] = main_cfg.scene.ANIMATED_CHARACTERS[0].__dict__

    # last, we regenerate main config file
    target_main_cfg_path = osp.join(tmp_dir, 'main_cfg.yaml')

    with open(target_main_cfg_path, 'w') as f:
        yaml.dump(convert_easydict_to_dict(main_cfg), f)

    print(f'>>> Regenerate config files successfully, the main config file stored in {target_main_cfg_path}')

    return target_main_cfg_path


if __name__ == '__main__':
    main_cfg = combine_cfg_and_args()
    main_cfg_path = reload_config_files(main_cfg)
    render.start(main_cfg_path)
    # shutil.rmtree(tmp_dir)
