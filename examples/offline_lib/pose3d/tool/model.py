import numpy as np
import numpy.typing as npt
import onnxruntime
import torch
from typing import Tuple


class PoseEstimator():
    def __init__(self, from_main_cfg=None, model_path: str = ''):
        assert model_path.endswith('.onnx'), 'In onnx inference mode, you should offer correct *.onnx file!!'
        self.main_cfg = from_main_cfg
        self.sesstion = onnxruntime.InferenceSession(model_path)

    def __call__(self, x: Tuple[npt.NDArray, torch.Tensor]):
        '''

        :param x: [N,T,V,C] for 2D pose sequence
        :return: [N,T,V,C] for 3D pose sequence
        '''
        if isinstance(x, torch.Tensor):
            x = x.detach().cpu().numpy()
        output_tuple = self.sesstion.run(['pose3d'], {'pose2d': x.astype(np.float32)}, )
        out_pose_3d = output_tuple[0]
        return out_pose_3d
