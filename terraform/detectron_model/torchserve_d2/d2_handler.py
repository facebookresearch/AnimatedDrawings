import os.path
import io, json, time
import numpy as np
import cv2
import torch, torchvision


class ModelHandler(object):
    """
    A base Model handler implementation.
    """

    def __init__(self):
        self.error = None
        self._context = None
        self.initialized = False


    def initialize(self, context):
        """
        Initialize model. This will be called during model loading time
        :param context: Initial context contains model server system properties.
        :return:
        """
        print("initializing starting")

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

        # Take the input data and pre-process it make it inference ready
        print("pre-processing started for a batch of {}".format(len(batch)))

        images = []

        # batch is a list of requests
        for request in batch:

            request_body = request.get("body")

            input_ = io.BytesIO(request_body)
            img = cv2.imdecode(np.fromstring(input_.read(), np.uint8), 1)
            images.append(img)

        print("pre-processing finished for a batch of {}".format(len(batch)))

        return images


    def inference(self, model_input):
        print("inference started for a batch of {}".format(len(model_input)))

        outputs = []
        for image in model_input:
            input_ = torch.Tensor(image).permute(2, 0, 1)
            output = self.model( input_)
            outputs.append(output)

        print("inference finished for a batch of {}".format(len(model_input)))

        return outputs


    def postprocess(self, inference_output):
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
        print("handling started")

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

