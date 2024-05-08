from .ViTPose_common import *

# Channel configuration
channel_cfg = dict(
    num_output_channels=14,
    dataset_joints=14,
    dataset_channel=[
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
    ],
    inference_channel=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])

# Set models channels
data_cfg['num_output_channels'] = channel_cfg['num_output_channels']
data_cfg['num_joints']= channel_cfg['dataset_joints']
data_cfg['dataset_channel']= channel_cfg['dataset_channel']
data_cfg['inference_channel']= channel_cfg['inference_channel']

names = ['small', 'base', 'large', 'huge']
for name in names:
    globals()[f'model_{name}']['keypoint_head']['out_channels'] = channel_cfg['num_output_channels']
