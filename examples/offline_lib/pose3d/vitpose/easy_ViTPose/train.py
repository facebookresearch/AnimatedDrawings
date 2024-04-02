# Copyright (c) OpenMMLab. All rights reserved.
import argparse
import copy
import os
import os.path as osp
import time
import warnings
import click
import yaml

from glob import glob

import torch
import torch.distributed as dist

from vit_utils.util import init_random_seed, set_random_seed
from vit_utils.dist_util import get_dist_info, init_dist
from vit_utils.logging import get_root_logger

import configs.ViTPose_small_coco_256x192 as s_cfg
import configs.ViTPose_base_coco_256x192 as b_cfg
import configs.ViTPose_large_coco_256x192 as l_cfg
import configs.ViTPose_huge_coco_256x192 as h_cfg

from vit_models.model import ViTPose
from datasets.COCO import COCODataset
from vit_utils.train_valid_fn import train_model

CUR_PATH = osp.dirname(__file__)

@click.command()
@click.option('--config-path', type=click.Path(exists=True), default='config.yaml', required=True, help='train config file path')
@click.option('--model-name', type=str, default='b', required=True, help='[b: ViT-B, l: ViT-L, h: ViT-H]')
def main(config_path, model_name):
        
    cfg = {'b':b_cfg,
           's':s_cfg,
           'l':l_cfg,
           'h':h_cfg}.get(model_name.lower())
    # Load config.yaml
    with open(config_path, 'r') as f:
        cfg_yaml = yaml.load(f, Loader=yaml.SafeLoader)
        
    for k, v in cfg_yaml.items():
        if hasattr(cfg, k):
            raise ValueError(f"Already exists {k} in config")
        else:
            cfg.__setattr__(k, v)

    # set cudnn_benchmark
    if cfg.cudnn_benchmark:
        torch.backends.cudnn.benchmark = True
    
    # Set work directory (session-level)
    if not hasattr(cfg, 'work_dir'):
        cfg.__setattr__('work_dir', f"{CUR_PATH}/runs/train")
        
    if not osp.exists(cfg.work_dir):
        os.makedirs(cfg.work_dir)
    session_list = sorted(glob(f"{cfg.work_dir}/*"))
    if len(session_list) == 0:
        session = 1
    else:
        session = int(os.path.basename(session_list[-1])) + 1
    session_dir = osp.join(cfg.work_dir, str(session).zfill(3))
    os.makedirs(session_dir)
    cfg.__setattr__('work_dir', session_dir)
        

    if cfg.autoscale_lr:
        # apply the linear scaling rule (https://arxiv.org/abs/1706.02677)
        cfg.optimizer['lr'] = cfg.optimizer['lr'] * len(cfg.gpu_ids) / 8

    # init distributed env first, since logger depends on the dist info.
    if cfg.launcher == 'none':
        distributed = False
        if len(cfg.gpu_ids) > 1:
            warnings.warn(
                f"We treat {cfg['gpu_ids']} as gpu-ids, and reset to "
                f"{cfg['gpu_ids'][0:1]} as gpu-ids to avoid potential error in "
                "non-distribute training time.")
            cfg.gpu_ids = cfg.gpu_ids[0:1]
    else:
        distributed = True
        init_dist(cfg.launcher, **cfg.dist_params)
        # re-set gpu_ids with distributed training mode
        _, world_size = get_dist_info()
        cfg.gpu_ids = range(world_size)

    # init the logger before other steps
    timestamp = time.strftime('%Y%m%d_%H%M%S', time.localtime())
    log_file = osp.join(session_dir, f'{timestamp}.log')
    logger = get_root_logger(log_file=log_file)

    # init the meta dict to record some important information such as
    # environment info and seed, which will be logged
    meta = dict()

    # log some basic info
    logger.info(f'Distributed training: {distributed}')

    # set random seeds
    seed = init_random_seed(cfg.seed)
    logger.info(f"Set random seed to {seed}, "
                f"deterministic: {cfg.deterministic}")
    set_random_seed(seed, deterministic=cfg.deterministic)
    meta['seed'] = seed

    # Set model
    model = ViTPose(cfg.model)
    if cfg.resume_from:
        # Load ckpt partially
        ckpt_state = torch.load(cfg.resume_from)['state_dict']
        ckpt_state.pop('keypoint_head.final_layer.bias')
        ckpt_state.pop('keypoint_head.final_layer.weight')
        model.load_state_dict(ckpt_state, strict=False)

        # freeze the backbone, leave the head to be finetuned
        model.backbone.frozen_stages = model.backbone.depth - 1
        model.backbone.freeze_ffn = True
        model.backbone.freeze_attn = True
        model.backbone._freeze_stages()
    
    # Set dataset
    datasets_train = COCODataset(
        root_path=cfg.data_root, 
        data_version="feet_train",
        is_train=True, 
        use_gt_bboxes=True,
        image_width=192, 
        image_height=256,
        scale=True, 
        scale_factor=0.35, 
        flip_prob=0.5, 
        rotate_prob=0.5, 
        rotation_factor=45., 
        half_body_prob=0.3,
        use_different_joints_weight=True, 
        heatmap_sigma=3, 
        soft_nms=False
        )
    
    datasets_valid = COCODataset(
        root_path=cfg.data_root, 
        data_version="feet_val",
        is_train=False, 
        use_gt_bboxes=True,
        image_width=192, 
        image_height=256,
        scale=False, 
        scale_factor=0.35, 
        flip_prob=0.5, 
        rotate_prob=0.5, 
        rotation_factor=45., 
        half_body_prob=0.3,
        use_different_joints_weight=True, 
        heatmap_sigma=3, 
        soft_nms=False
        )

    train_model(
        model=model,
        datasets_train=datasets_train,
        datasets_valid=datasets_valid,
        cfg=cfg,
        distributed=distributed,
        validate=cfg.validate,
        timestamp=timestamp,
        meta=meta
        )


if __name__ == '__main__':
    main()
