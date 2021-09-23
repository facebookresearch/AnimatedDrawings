# Some basic setup:
import detectron2
import os.path
import sys, io, json, time, random
import numpy as np
import cv2
import base64

# Setup detectron2 logger
from detectron2.utils.logger import setup_logger

setup_logger()

# import some common detectron2 utilities
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from os import path
from json import JSONEncoder

import torch, torchvision


class ModelHandler(object):
    """
    A base Model handler implementation.
    """

    def __init__(self):
        self.error = None
        self.initialized = False
        self.model_file = "../torchscript/model.ts"
        self.config_file = "../torchscript/model_config.yaml"


    def initialize(self, context):
        """
        Initialize model. This will be called during model loading time
        :param context: Initial context contains model server system properties.
        :return:
        """
        print("initializing starting")

        print(f"cwd is {os.getcwd()}")

        #  load the model
        self.manifest = context.manifest

        properties = context.system_properties
        model_dir = properties.get("model_dir")
        self.device = torch.device("cuda:" + str(properties.get("gpu_id")) if torch.cuda.is_available() else "cpu")

        # Read model serialize/pt file
        serialized_file = self.manifest['model']['serializedFile']
        model_pt_path = os.path.join(model_dir, serialized_file)
        if not os.path.isfile(model_pt_path):
            raise RuntimeError(f"Missing the model.pt file: {model_pt_path}")

        self.model = torch.jit.load(model_pt_path)

        self.initialized = True

        print("initialized")


    def preprocess(self, batch):
        # assert self._batch_size == len(batch), "Invalid input batch size: {}".format(len(batch))

        # Take the input data and pre-process it make it inference ready
        print("pre-processing started for a batch of {}".format(len(batch)))

        images = []

        # batch is a list of requests
        for request in batch:

            # each item in the list is a dictionary with a single body key, get the body of the request
            request_body = request.get("body")

            # read the bytes of the image
            input = io.BytesIO(request_body)

            # get our image
            img = cv2.imdecode(np.fromstring(input.read(), np.uint8), 1)

            # add the image to our list
            images.append(img)

        print("pre-processing finished for a batch of {}".format(len(batch)))

        return images

    def inference(self, model_input):
        """
        Internal inference methods
        :param model_input: transformed model input data
        :return: list of inference output in NDArray
        """

        # Do some inference call to engine here and return output
        print("inference started for a batch of {}".format(len(model_input)))

        outputs = []

        for image in model_input:

            input_ = torch.Tensor(image).permute(2, 0, 1)

            output = self.model( input_)

            outputs.append(output)

        print("inference finished for a batch of {}".format(len(model_input)))

        return outputs

    def postprocess(self, inference_output):

        """
        Return predict result in batch.
        :param inference_output: list of inference output
        :return: list of predict results
        """
        start_time = time.time()

        print("post-processing started at {} for a batch of {}".format(start_time, len(inference_output)))

        responses = []

        for boxes, class_, masks, scores, img_dims in inference_output:

            responses_json = {'classes': class_.tolist(), 'scores': scores.tolist(), "boxes": boxes.tolist()}

            responses.append(json.dumps(responses_json))

        elapsed_time = time.time() - start_time

        print("post-processing finished for a batch of {} in {}".format(len(inference_output), elapsed_time))

        return responses

    def handle(self, data, context):
        """
        Call preprocess, inference and post-process functions
        :param data: input data
        :param context: mms context
        """
        print("handling started")

        # process the data through our inference pipeline
        model_input = self.preprocess(data)
        model_out = self.inference(model_input)
        output = self.postprocess(model_out)

        print("handling finished")

        return output


_service = ModelHandler()


def handle(data, context):
    if not _service.initialized:
        _service.initialize(context)

    if data is None:
        return None

    return _service.handle(data, context)

