import os.path as osp

import torch
import torch.nn as nn

from vit_models.losses import JointsMSELoss
from vit_models.optimizer import LayerDecayOptimizer

from torch.nn.parallel import DataParallel, DistributedDataParallel
from torch.nn.utils import clip_grad_norm_
from torch.optim import AdamW
from torch.optim.lr_scheduler import LambdaLR, MultiStepLR
from torch.utils.data import DataLoader, Dataset
from torch.utils.data.distributed import DistributedSampler
from torch.cuda.amp import autocast, GradScaler
from tqdm import tqdm
from time import time

from vit_utils.dist_util import get_dist_info, init_dist
from vit_utils.logging import get_root_logger

@torch.no_grad()
def valid_model(model: nn.Module, dataloaders: DataLoader, criterion: nn.Module, cfg: dict) -> None:
    total_loss = 0
    total_metric = 0
    model.eval()
    for dataloader in dataloaders:
        for batch_idx, batch in enumerate(dataloader):
            images, targets, target_weights, __ = batch
            images = images.to('cuda')
            targets = targets.to('cuda')
            target_weights = target_weights.to('cuda')
            
            outputs = model(images)
            loss = criterion(outputs, targets, target_weights)
            total_loss += loss.item()
            
    avg_loss = total_loss/(len(dataloader)*len(dataloaders))
    return avg_loss
 
def train_model(model: nn.Module, datasets_train: Dataset, datasets_valid: Dataset, cfg: dict, distributed: bool, validate: bool,  timestamp: str, meta: dict) -> None:
    logger = get_root_logger()
    
    # Prepare data loaders
    datasets_train = datasets_train if isinstance(datasets_train, (list, tuple)) else [datasets_train]
    datasets_valid = datasets_valid if isinstance(datasets_valid, (list, tuple)) else [datasets_valid]
    
    if distributed:
        samplers_train = [DistributedSampler(ds, num_replicas=len(cfg.gpu_ids), rank=torch.cuda.current_device(), shuffle=True, drop_last=False) for ds in datasets_train]
        samplers_valid = [DistributedSampler(ds, num_replicas=len(cfg.gpu_ids), rank=torch.cuda.current_device(), shuffle=False, drop_last=False) for ds in datasets_valid]
    else:
        samplers_train = [None for ds in datasets_train]
        samplers_valid = [None for ds in datasets_valid]
    
    dataloaders_train = [DataLoader(ds, batch_size=cfg.data['samples_per_gpu'], shuffle=True, sampler=sampler, num_workers=cfg.data['workers_per_gpu'], pin_memory=False) for ds, sampler in zip(datasets_train, samplers_train)]
    dataloaders_valid = [DataLoader(ds, batch_size=cfg.data['samples_per_gpu'], shuffle=False, sampler=sampler, num_workers=cfg.data['workers_per_gpu'], pin_memory=False) for ds, sampler in zip(datasets_valid, samplers_valid)]

    # put model on gpus
    if distributed:
        find_unused_parameters = cfg.get('find_unused_parameters', False)
        # Sets the `find_unused_parameters` parameter in
        # torch.nn.parallel.DistributedDataParallel

        model = DistributedDataParallel(
            module=model, 
            device_ids=[torch.cuda.current_device()], 
            broadcast_buffers=False, 
            find_unused_parameters=find_unused_parameters)
    else:
        model = DataParallel(model, device_ids=cfg.gpu_ids)

    # Loss function
    criterion = JointsMSELoss(use_target_weight=cfg.model['keypoint_head']['loss_keypoint']['use_target_weight'])
    
    # Optimizer
    optimizer = AdamW(model.parameters(), lr=cfg.optimizer['lr'], betas=cfg.optimizer['betas'], weight_decay=cfg.optimizer['weight_decay'])
    
    # Layer-wise learning rate decay
    lr_mult = [cfg.optimizer['paramwise_cfg']['layer_decay_rate']] * cfg.optimizer['paramwise_cfg']['num_layers']
    layerwise_optimizer = LayerDecayOptimizer(optimizer, lr_mult)
    
    
    # Learning rate scheduler (MultiStepLR)
    milestones = cfg.lr_config['step']
    gamma = 0.1
    scheduler = MultiStepLR(optimizer, milestones, gamma)

    # Warm-up scheduler
    num_warmup_steps = cfg.lr_config['warmup_iters']  # Number of warm-up steps
    warmup_factor = cfg.lr_config['warmup_ratio']  # Initial learning rate = warmup_factor * learning_rate
    warmup_scheduler = LambdaLR(
        optimizer,
        lr_lambda=lambda step: warmup_factor + (1.0 - warmup_factor) * step / num_warmup_steps
    )
    
    # AMP setting
    if cfg.use_amp:
        logger.info("Using Automatic Mixed Precision (AMP) training...")
        # Create a GradScaler object for FP16 training
        scaler = GradScaler()
    
    # Logging config
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    logger.info(f'''\n
    #========= [Train Configs] =========#
    # - Num GPUs: {len(cfg.gpu_ids)}
    # - Batch size (per gpu): {cfg.data['samples_per_gpu']}
    # - LR: {cfg.optimizer['lr']: .6f}
    # - Num params: {total_params:,d}
    # - AMP: {cfg.use_amp}
    #===================================# 
    ''')
    
    global_step = 0
    for dataloader in dataloaders_train:
        for epoch in range(cfg.total_epochs):
            model.train()
            train_pbar = tqdm(dataloader)
            total_loss = 0
            tic = time()
            for batch_idx, batch in enumerate(train_pbar):
                layerwise_optimizer.zero_grad()
                    
                images, targets, target_weights, __ = batch
                images = images.to('cuda')
                targets = targets.to('cuda')
                target_weights = target_weights.to('cuda')
                
                if cfg.use_amp:
                    with autocast():
                        outputs = model(images)
                        loss = criterion(outputs, targets, target_weights)
                    scaler.scale(loss).backward()
                    clip_grad_norm_(model.parameters(), **cfg.optimizer_config['grad_clip'])
                    scaler.step(layerwise_optimizer)
                    scaler.update()
                else:
                    outputs = model(images)
                    loss = criterion(outputs, targets, target_weights)
                    loss.backward()
                    clip_grad_norm_(model.parameters(), **cfg.optimizer_config['grad_clip'])
                    layerwise_optimizer.step()
                
                if global_step < num_warmup_steps:
                    warmup_scheduler.step()
                global_step += 1
                
                total_loss += loss.item()
                train_pbar.set_description(f"🏋️> Epoch [{str(epoch).zfill(3)}/{str(cfg.total_epochs).zfill(3)}] | Loss {loss.item():.4f} | LR {optimizer.param_groups[0]['lr']:.6f} | Step")
            scheduler.step()
            
            avg_loss_train = total_loss/len(dataloader)
            logger.info(f"[Summary-train] Epoch [{str(epoch).zfill(3)}/{str(cfg.total_epochs).zfill(3)}] | Average Loss (train) {avg_loss_train:.4f} --- {time()-tic:.5f} sec. elapsed")
            ckpt_name = f"epoch{str(epoch).zfill(3)}.pth"
            ckpt_path = osp.join(cfg.work_dir, ckpt_name)
            torch.save(model.module.state_dict(), ckpt_path)

            # validation
            if validate:
                tic2 = time()
                avg_loss_valid = valid_model(model, dataloaders_valid, criterion, cfg)
                logger.info(f"[Summary-valid] Epoch [{str(epoch).zfill(3)}/{str(cfg.total_epochs).zfill(3)}] | Average Loss (valid) {avg_loss_valid:.4f} --- {time()-tic2:.5f} sec. elapsed")
