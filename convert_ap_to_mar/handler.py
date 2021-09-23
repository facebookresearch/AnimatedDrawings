from ts.torch_handler.base_handler import BaseHandler

from alphapose.utils.file_detector import FileDetectionLoader
from alphapose.utils.transforms import get_func_heatmap_to_coord
from alphapose.utils.config import update_config
from alphapose.utils.writer import DataWriter

import torch
import numpy as np
import io
import cv2
import json
import shutil

import os

class ModelHandler(BaseHandler):
    class Struct:
        def __init__(self, **entries):
            self.__dict__.update(entries)
    """
    A custom model handler implementation.
    """

    def __init__(self):
        self._context = None
        self.initialized = False
        self.explain = False
        self.target = 0

    def initialize(self, context):
        """
        Initialize model. This will be called during model loading time
        :param context: Initial context contains model server system properties.
        :return:
        """
        self._context = context

        self.args = self.Struct(**{'qsize': 1024, 'cfg': None, 'vis_fast': False, 'outputpath': 'examples/res/', 'vis': False, 'video': '', 'pose_flow': False, 'save_video': False, 'detfile': '', 'checkpoint': None, 'inputpath': '', 'detector': 'yolo', 'profile': False, 'inputimg': '', 'format': None, 'inputlist': '', 'min_box_area': 0, 'eval': False, 'posebatch': 80, 'gpus': '-1', 'webcam': -1, 'sp': True, 'flip': False, 'save_img': False, 'showbox': False, 'debug': False, 'detbatch': 5, 'pose_track': False, 'device': 'cpu'})

        properties = context.system_properties
        model_dir = properties.get("model_dir")
        self.cfg = update_config(os.path.join(model_dir, 'pose_detection.yaml'))

        self.manifest = context.manifest
        serialized_file = self.manifest['model']['serializedFile']
        model_pt_path = os.path.join(model_dir, serialized_file)
        if not os.path.isfile(model_pt_path):
            raise RuntimeError(f"Missing the model.pt file: {model_pt_path}")
   
        self.pose_model = torch.jit.load(model_pt_path)

        self.writer = DataWriter(self.cfg, self.args, save_video=False, queueSize=self.args.qsize).start()

        self.initialized = True

    def preprocess(self, batch):

        request_uuid = batch[0].get("uuid").decode("utf-8")

        request_image = batch[0].get("image")
        image_bytes = io.BytesIO(request_image)
        image = cv2.imdecode(np.fromstring(image_bytes.read(), np.uint8), 1)

        work_dir = os.path.join(os.getcwd(), request_uuid)
        image_path = os.path.join(work_dir, 'cropped_img.png')
        det_path = os.path.join(work_dir, 'sketch-DET.json')

        os.mkdir(work_dir)

        cv2.imwrite(image_path, image)

        sketch_det = [{
            "category_id": 1,
            "score": 0.9,
            "bbox": [int(image.shape[1]/2), int(image.shape[0]/2), image.shape[1], image.shape[0]],
            "image_id": image_path
        }]
        with open(det_path, 'w') as f:
            json.dump(sketch_det, f)

        return det_path, work_dir


    def inference(self, input_source):

        self.det_loader = FileDetectionLoader(input_source, self.cfg, self.args)
        self.det_worker = self.det_loader.start()

        with torch.no_grad():
            (inps, orig_img, im_name, boxes, scores, ids, cropped_boxes) = self.det_loader.read()
            inps = inps.to('cpu')
            hm = self.pose_model(inps)
            return (hm.numpy(), cropped_boxes)


    def postprocess(self, inference_output):

        self.eval_joints = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        hm_size = self.cfg.DATA_PRESET.HEATMAP_SIZE
        norm_type = self.cfg.LOSS.get('NORM_TYPE', None)

        hm_data, cropped_boxes = inference_output
        self.heatmap_to_coord = get_func_heatmap_to_coord(self.cfg)

        pose_coords, pose_scores = [], []
        for i in range(hm_data.shape[0]):
            bbox = cropped_boxes[i].tolist()
            pose_coord, pose_score = self.heatmap_to_coord(hm_data[i][self.eval_joints], bbox, hm_shape=hm_size, norm_type=norm_type)
            pose_coords.append(torch.from_numpy(pose_coord).unsqueeze(0))
            pose_scores.append(torch.from_numpy(pose_score).unsqueeze(0))
        
        preds_img = torch.cat(pose_coords)
        preds_scores = torch.cat(pose_scores)
        keypoints = torch.cat((preds_img, preds_scores), 2).numpy().flatten().tolist()


        return [{'keypoints':keypoints}]



    def handle(self, data, context):
        """
        Invoke by TorchServe for prediction request.
        Do pre-processing of data, prediction using model and postprocessing of prediciton output
        :param data: Input data for prediction
        :param context: Initial context contains model server system properties.
        :return: prediction output
        """

        if not self.initialized:
            self.initialize()

        model_input, work_dir = self.preprocess(data)
        model_output = self.inference(model_input)

        shutil.rmtree(work_dir)

        return self.postprocess(model_output)
