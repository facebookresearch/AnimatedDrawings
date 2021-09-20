from ts.torch_handler.base_handler import BaseHandler

from alphapose.utils.file_detector import FileDetectionLoader
from alphapose.utils.transforms import get_func_heatmap_to_coord
from alphapose.models import builder
from alphapose.utils.config import update_config
from alphapose.utils.writer import DataWriter

import torch

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


        cfg ='/home/model-server/rig/server/configs/pose_detection.yaml'
        self.cfg = update_config(cfg)

        properties = context.system_properties
        self.manifest = context.manifest
        model_dir = properties.get("model_dir")
        serialized_file = self.manifest['model']['serializedFile']
        model_pt_path = os.path.join(model_dir, serialized_file)
        if not os.path.isfile(model_pt_path):
            raise RuntimeError(f"Missing the model.pt file: {model_pt_path}")
   
        self.pose_model = torch.jit.load(model_pt_path)

        self.writer = DataWriter(self.cfg, self.args, save_video=False, queueSize=self.args.qsize).start()


        #self.pose_model = builder.build_sppe(cfg.MODEL, preset_cfg=cfg.DATA_PRESET)

        #print(f'Loading pose model from {args.checkpoint}...')
        #self.pose_model.load_state_dict(torch.load(args.checkpoint, map_location=args.device))

        self.initialized = True
        #  load the model, refer 'custom handler class' above for details

    def preprocess(self, data):
        """
        Transform raw input into model input data.
        :param batch: list of raw requests, should match batch size
        :return: list of preprocessed model input data
        """


        # # Take the input data and make it inference ready
        preprocessed_data = data[0].get("det_file_loc").decode("utf-8")

        return preprocessed_data


    def inference(self, input_source):
        """
        Internal inference methods
        :param model_input: transformed model input data
        :return: list of inference output in NDArray
        """
        #self.det_loader = FileDetectionLoader(input_source, self.cfg, self.args)
        self.det_loader = FileDetectionLoader(input_source, self.cfg, self.args)
        self.det_worker = self.det_loader.start()


        with torch.no_grad():
            (inps, orig_img, im_name, boxes, scores, ids, cropped_boxes) = self.det_loader.read()
            inps = inps.to('cpu')
            hm = self.pose_model(inps)
            return (hm.numpy(), cropped_boxes)


        # # Do some inference call to engine here and return output
        # model_output = self.model.forward(model_input)
        # return model_output

    def postprocess(self, inference_output):
        """
        Return inference result.
        :param inference_output: list of inference output
        :return: list of predict results
        """
        # # Take output from network and post-process to desired format
        postprocess_output = inference_output

        self.eval_joints = EVAL_JOINTS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        hm_size = self.cfg.DATA_PRESET.HEATMAP_SIZE
        norm_type = self.cfg.LOSS.get('NORM_TYPE', None)

        hm_data, cropped_boxes = inference_output
        self.heatmap_to_coord = get_func_heatmap_to_coord(self.cfg)

        pose_coords = []
        pose_scores = []
        for i in range(hm_data.shape[0]):
            bbox = cropped_boxes[i].tolist()
            pose_coord, pose_score = self.heatmap_to_coord(hm_data[i][self.eval_joints], bbox, hm_shape=hm_size, norm_type=norm_type)
            pose_coords.append(torch.from_numpy(pose_coord).unsqueeze(0))
            pose_scores.append(torch.from_numpy(pose_score).unsqueeze(0))
        
        preds_img = torch.cat(pose_coords)
        preds_scores = torch.cat(pose_scores)


        #self.writer.save(boxes, scores, ids, hm, cropped_boxes, orig_img, im_name)
        #pose = self.writer.start().update()
        ret = torch.cat((preds_img, preds_scores), 2)
        return [{'keypoints':preds_img.numpy().tolist(), 'confidence':preds_scores.numpy().tolist()}] # -1 # pose


        return postprocess_output

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

        model_input = self.preprocess(data)
        model_output = self.inference(model_input)
        return self.postprocess(model_output)
        #return model_output