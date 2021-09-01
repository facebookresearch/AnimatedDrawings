import torch, torchvision
import numpy as np
import os, json, cv2, sys, pickle
from pathlib import Path
from PIL import Image

import shutil
sys.path.insert(0, '/private/home/hjessmith/utils_j')
import d2prediction_utils as d2p

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
    input_img = os.path.join(sys.argv[1], 'image.png')
    output_dir = sys.argv[1]  

    #Path(output_dir).mkdir(exist_ok=True, parents=True)

    cfg = get_cfg()
    cfg.merge_from_file("/private/home/hjessmith/scripts/04-19-2021/humanoid_detection.yaml")
    predictor = DefaultPredictor(cfg)

    prediction_img, instances = detect(input_img)
    prediction_img.save(os.path.join(output_dir, 'd2_viz.png'))		

    bb = d2p.get_bb_from_multiple_bb(instances, 25)
    with open(os.path.join(output_dir, 'bb.json'), 'w') as f:
        json.dump(bb, f)

    #pickle_name = os.path.join(output_dir, fn[:-3]+"pickle")
    #with open(pickle_name, 'wb') as handle:
    #        pickle.dump(instances, handle)
