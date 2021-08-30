import torch, torchvision
import numpy as np
import os, json, cv2, sys, pickle
from pathlib import Path
from PIL import Image

import detectron2
from detectron2.utils.logger import setup_logger
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2.structures import BoxMode
from detectron2.utils.visualizer import ColorMode

setup_logger()

def detect(image):
    im = cv2.imread(image)
    outputs = predictor(im)
    v = Visualizer(im[:, :, ::-1], scale=1.0, instance_mode=ColorMode.IMAGE_BW)
    out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
    return Image.fromarray(out.get_image()[:, :, :]), outputs["instances"].to("cpu")

if __name__ == '__main__':
    input_dir = sys.argv[1]  
    output_dir = sys.argv[2]  
    humanoid_detection_yaml = sys.argv[3]
    humanoid_detection_weights_loc = sys.argv[4]

    Path(output_dir).mkdir(exist_ok=True, parents=True)

    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file("Base-RCNN-FPN.yaml"))
    cfg.merge_from_file(humanoid_detection_yaml)
    cfg.MODEL.WEIGHTS= humanoid_detection_weights_loc
    predictor = DefaultPredictor(cfg)

    for fn in os.listdir(input_dir):
            if not fn.endswith('.jpg') and not fn.endswith('.png'):
                    continue
            prediction_img, instances = detect(os.path.join(input_dir, fn))
            prediction_img.save(os.path.join(output_dir, fn))		

            pickle_name = os.path.join(output_dir, fn[:-3]+"pickle")
            with open(pickle_name, 'wb') as handle:
                    pickle.dump(instances, handle)
