import os.path as osp
import sys

sys.path.append(osp.abspath(osp.join(osp.dirname(__file__))))
sys.path.append(osp.abspath(osp.join(osp.dirname(__file__), '..')))
sys.path.append(osp.abspath(osp.join(osp.dirname(__file__), '..', '..')))

import torch
import numpy as np
import glob
import os
import io
import math
import random
import json
import pickle
import math
from torch.utils.data import Dataset, DataLoader
from .utils_data import crop_scale
import imageio


# transfer halpe -> h36m format
def halpe2h36m(x):
    '''
        Input: x (T x V x C)  
       //Halpe 26 body keypoints
    {0,  "Nose"},
    {1,  "LEye"},
    {2,  "REye"},
    {3,  "LEar"},
    {4,  "REar"},
    {5,  "LShoulder"},
    {6,  "RShoulder"},
    {7,  "LElbow"},
    {8,  "RElbow"},
    {9,  "LWrist"},
    {10, "RWrist"},
    {11, "LHip"},
    {12, "RHip"},
    {13, "LKnee"},
    {14, "Rknee"},
    {15, "LAnkle"},
    {16, "RAnkle"},
    {17,  "Head"},
    {18,  "Neck"},
    {19,  "Hip"},
    {20, "LBigToe"},
    {21, "RBigToe"},
    {22, "LSmallToe"},
    {23, "RSmallToe"},
    {24, "LHeel"},
    {25, "RHeel"},
    '''
    T, V, C = x.shape
    y = np.zeros([T, 17, C])
    y[:, 0, :] = x[:, 19, :]
    y[:, 1, :] = x[:, 12, :]
    y[:, 2, :] = x[:, 14, :]
    y[:, 3, :] = x[:, 16, :]
    y[:, 4, :] = x[:, 11, :]
    y[:, 5, :] = x[:, 13, :]
    y[:, 6, :] = x[:, 15, :]
    y[:, 7, :] = (x[:, 18, :] + x[:, 19, :]) * 0.5
    y[:, 8, :] = x[:, 18, :]
    y[:, 9, :] = x[:, 0, :]
    y[:, 10, :] = x[:, 17, :]
    y[:, 11, :] = x[:, 5, :]
    y[:, 12, :] = x[:, 7, :]
    y[:, 13, :] = x[:, 9, :]
    y[:, 14, :] = x[:, 6, :]
    y[:, 15, :] = x[:, 8, :]
    y[:, 16, :] = x[:, 10, :]
    return y


# transfer coco -> h36m format
def coco2h36m(x):
    '''
        Input: x (M x T x V x C) or (T x V x C)

        COCO: {0-nose 1-Leye 2-Reye 3-Lear 4Rear 5-Lsho 6-Rsho 7-Lelb 8-Relb 9-Lwri 10-Rwri 11-Lhip 12-Rhip 13-Lkne 14-Rkne 15-Lank 16-Rank}

        H36M:
        0: 'root',
        1: 'rhip',
        2: 'rkne',
        3: 'rank',
        4: 'lhip',
        5: 'lkne',
        6: 'lank',
        7: 'belly',
        8: 'neck',
        9: 'nose',
        10: 'head',
        11: 'lsho',
        12: 'lelb',
        13: 'lwri',
        14: 'rsho',
        15: 'relb',
        16: 'rwri'
    '''
    y = np.zeros(x.shape)
    y[..., 0, :] = (x[..., 11, :] + x[..., 12, :]) * 0.5
    y[..., 1, :] = x[..., 12, :]
    y[..., 2, :] = x[..., 14, :]
    y[..., 3, :] = x[..., 16, :]
    y[..., 4, :] = x[..., 11, :]
    y[..., 5, :] = x[..., 13, :]
    y[..., 6, :] = x[..., 15, :]
    y[..., 8, :] = (x[..., 5, :] + x[..., 6, :]) * 0.5
    y[..., 7, :] = (y[..., 0, :] + y[..., 8, :]) * 0.5
    y[..., 9, :] = x[..., 0, :]
    y[..., 10, :] = (x[..., 1, :] + x[..., 2, :]) * 0.5
    y[..., 11, :] = x[..., 5, :]
    y[..., 12, :] = x[..., 7, :]
    y[..., 13, :] = x[..., 9, :]
    y[..., 14, :] = x[..., 6, :]
    y[..., 15, :] = x[..., 8, :]
    y[..., 16, :] = x[..., 10, :]
    return y


def read_2dkeypoints_from_numpy(numpy_data, vid_size, scale_range, focus, joints_format):
    '''
    :param numpy_data: [T,V,C=2或3]
    :param vid_size:
    :param scale_range:
    :param focus:
    :param joints_format:
    :return:
    '''
    if joints_format.lower() == 'coco':
        kpts_all = coco2h36m(numpy_data)
    elif joints_format.lower() == 'halpe':
        kpts_all = halpe2h36m(numpy_data)
    else:
        raise NotImplementedError

    if vid_size:
        w, h = vid_size
        scale = min(w, h) / 2.0
        kpts_all[:, :, :2] = kpts_all[:, :, :2] - np.array([w, h]) / 2.0
        kpts_all[:, :, :2] = kpts_all[:, :, :2] / scale
        motion = kpts_all
    if scale_range:
        motion = crop_scale(kpts_all, scale_range)
    return motion.astype(np.float32)


class WildDetNumpyDataset(Dataset):
    def __init__(self, numpy_data, clip_len=243, vid_size=None, scale_range=None, focus=None, format='coco'):
        self.numpy_data = numpy_data
        self.clip_len = clip_len
        # [T,V,C]
        self.vid_all = read_2dkeypoints_from_numpy(numpy_data, vid_size, scale_range, focus, format)

    def __len__(self):
        'Denotes the total number of samples'
        return math.ceil(len(self.vid_all) / self.clip_len)

    def total_frame(self):
        ':return T'
        return self.vid_all.shape[0]

    def __getitem__(self, index):
        'Generates one sample of data'
        st = index * self.clip_len
        end = min((index + 1) * self.clip_len, len(self.vid_all))
        cur_output = self.vid_all[st:end]
        cur_T = cur_output.shape[0]
        if cur_T < self.clip_len:
            pad_right = self.clip_len - cur_T
            cur_output = np.pad(cur_output, ((0, pad_right), (0, 0), (0, 0)), mode='edge')
        return cur_output
