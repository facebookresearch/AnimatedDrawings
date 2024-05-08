import os
import torch
import torch.nn.functional as F
import numpy as np
import copy


# transfer from in [-1,1]
def crop_scale(motion, scale_range=[1, 1]):
    '''
        Motion: [(M), T, 17, 3]. [M,T,V,C]
        Normalize to [-1, 1]
    '''
    result = copy.deepcopy(motion)
    valid_coords = motion[motion[..., 2] != 0][:, :2]
    if len(valid_coords) < 4:
        return np.zeros(motion.shape)
    xmin = min(valid_coords[:, 0])
    xmax = max(valid_coords[:, 0])
    ymin = min(valid_coords[:, 1])
    ymax = max(valid_coords[:, 1])
    ratio = np.random.uniform(low=scale_range[0], high=scale_range[1], size=1)[0]
    scale = max(xmax - xmin, ymax - ymin) * ratio
    if scale == 0:
        return np.zeros(motion.shape)
    xs = (xmin + xmax - scale) / 2
    ys = (ymin + ymax - scale) / 2
    result[..., :2] = (motion[..., :2] - [xs, ys]) / scale
    result[..., :2] = (result[..., :2] - 0.5) * 2
    result = np.clip(result, -1, 1)
    return result


def crop_scale_3d(motion, scale_range=[1, 1]):
    '''
        Motion: [T, 17, 3]. (x, y, z)
        Normalize to [-1, 1]
        Z is relative to the first frame's root.
    '''
    result = copy.deepcopy(motion)
    result[:, :, 2] = result[:, :, 2] - result[0, 0, 2]
    xmin = np.min(motion[..., 0])
    xmax = np.max(motion[..., 0])
    ymin = np.min(motion[..., 1])
    ymax = np.max(motion[..., 1])
    ratio = np.random.uniform(low=scale_range[0], high=scale_range[1], size=1)[0]
    scale = max(xmax - xmin, ymax - ymin) / ratio
    if scale == 0:
        return np.zeros(motion.shape)
    xs = (xmin + xmax - scale) / 2
    ys = (ymin + ymax - scale) / 2
    result[..., :2] = (motion[..., :2] - [xs, ys]) / scale
    result[..., 2] = result[..., 2] / scale
    result = (result - 0.5) * 2
    return result


def flip_data(data):
    """
    horizontal flip
        data: [N, F, 17, D] or [F, 17, D]. X (horizontal coordinate) is the first channel in D.
    Return
        result: same
    """
    left_joints = [4, 5, 6, 11, 12, 13]
    right_joints = [1, 2, 3, 14, 15, 16]
    flipped_data = copy.deepcopy(data)
    flipped_data[..., 0] *= -1  # flip x of all joints
    flipped_data[..., left_joints + right_joints, :] = flipped_data[..., right_joints + left_joints, :]
    return flipped_data
