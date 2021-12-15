from ts.torch_handler.base_handler import BaseHandler

import torch
import numpy as np
import io
import cv2
import json
import shutil
import os

INPUT_SIZE = [256, 192]


class ModelHandler(BaseHandler):

    def __init__(self):
        self.initialized = False
        self.explain = False
        self.target = 0
        self.input_size = INPUT_SIZE

    def initialize(self, context):

        model_dir = context.system_properties.get("model_dir")

        serialized_file = context.manifest['model']['serializedFile']
        model_pt_path = os.path.join(model_dir, serialized_file)

        if not os.path.isfile(model_pt_path):
            raise RuntimeError(f"Missing the model.pt file: {model_pt_path}")

        self.device = torch.device("cuda:" + str(context.system_properties.get("gpu_id")) if torch.cuda.is_available() else "cpu")
        print(f'self.device is {self.device}')

        self.pose_model = torch.jit.load(model_pt_path, map_location=self.device)
        if str(self.device) != "cpu":
            self.pose_model = self.pose_model.half()

        self.initialized = True


    def preprocess(self, batch):

        images = []
        bboxes = np.empty([len(batch), 4])

        for idx, request in enumerate(batch):
            image_bytes = io.BytesIO(request.get("image"))
            image = cv2.imdecode(np.fromstring(image_bytes.read(), np.uint8), 1)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            images.append(image)

            bboxes[idx] = [0, 0, image.shape[1], image.shape[0]]

        inputs = torch.zeros(bboxes.shape[0], 3, *self.input_size)
        cropped_boxes = torch.zeros(bboxes.shape[0], 4)

        for idx, image in enumerate(images):
            box = bboxes[idx]
            inputs[idx], cropped_box = test_transform(image, box)
            cropped_boxes[idx] = torch.FloatTensor(cropped_box)

        return inputs, cropped_boxes


    def inference(self, inputs):

        inputs = inputs.to(self.device)
        if str(self.device) != "cpu":
            inputs = inputs.half()

        outputs = self.pose_model(inputs)
        if str(self.device) != "cpu":
            outputs = outputs.cpu()

        return outputs.detach().numpy()


    def postprocess(self, inference_output, cropped_boxes):

        self.eval_joints = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]

        hm_data = inference_output

        all_keypoints= []
        for i in range(hm_data.shape[0]):

            pose_coords, pose_scores = [], []

            bbox = cropped_boxes[i].tolist()

            pose_coord, pose_score = heatmap_to_coord_simple(hm_data[i][self.eval_joints], bbox)

            pose_coords.append(torch.from_numpy(pose_coord).unsqueeze(0))
            pose_scores.append(torch.from_numpy(pose_score).unsqueeze(0))

            preds_img = torch.cat(pose_coords)
            preds_scores = torch.cat(pose_scores)
            if str(self.device) != "cpu":
                preds_img = preds_img.half()
                preds_scores = preds_scores.half()

            keypoints = torch.cat((preds_img, preds_scores), 2).numpy().flatten().tolist()

            all_keypoints.append({'keypoints':keypoints})

        return all_keypoints


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

        inputs, cropped_boxes = self.preprocess(data)

        model_output = self.inference(inputs)

        return self.postprocess(model_output, cropped_boxes)

""" Functions below are adapted from Alphapose. Necessary to preprocess and postprocess """

def im_to_torch(img):
    img = np.transpose(img, (2, 0, 1))  # C*H*W
    img = torch.from_numpy(img).float()

    if img.max() > 1:
        img /= 255

    return img


def _center_scale_to_box(center, scale):
    pixel_std = 1.0
    w = scale[0] * pixel_std
    h = scale[1] * pixel_std
    xmin = center[0] - w * 0.5
    ymin = center[1] - h * 0.5
    xmax = xmin + w
    ymax = ymin + h
    bbox = [xmin, ymin, xmax, ymax]
    return bbox


def get_3rd_point(a, b):
    """Return vector c that perpendicular to (a - b)."""
    direct = a - b
    return b + np.array([-direct[1], direct[0]], dtype=np.float32)


def get_dir(src_point, rot_rad):
    """Rotate the point by `rot_rad` degree."""
    sn, cs = np.sin(rot_rad), np.cos(rot_rad)

    src_result = [0, 0]
    src_result[0] = src_point[0] * cs - src_point[1] * sn
    src_result[1] = src_point[0] * sn + src_point[1] * cs

    return src_result


def get_affine_transform(center, scale, rot, output_size, shift=np.array([0, 0], dtype=np.float32), inv=0):
    if not isinstance(scale, np.ndarray) and not isinstance(scale, list):
        scale = np.array([scale, scale])

    scale_tmp = scale
    src_w = scale_tmp[0]
    dst_w = output_size[0]
    dst_h = output_size[1]

    rot_rad = np.pi * rot / 180
    src_dir = get_dir([0, src_w * -0.5], rot_rad)
    dst_dir = np.array([0, dst_w * -0.5], np.float32)

    src = np.zeros((3, 2), dtype=np.float32)
    dst = np.zeros((3, 2), dtype=np.float32)
    src[0, :] = center + scale_tmp * shift
    src[1, :] = center + src_dir + scale_tmp * shift
    dst[0, :] = [dst_w * 0.5, dst_h * 0.5]
    dst[1, :] = np.array([dst_w * 0.5, dst_h * 0.5]) + dst_dir

    src[2:, :] = get_3rd_point(src[0, :], src[1, :])
    dst[2:, :] = get_3rd_point(dst[0, :], dst[1, :])

    if inv:
        trans = cv2.getAffineTransform(np.float32(dst), np.float32(src))
    else:
        trans = cv2.getAffineTransform(np.float32(src), np.float32(dst))

    return trans


def _box_to_center_scale(x, y, w, h, aspect_ratio=1.0, scale_mult=1.25):
    """Convert box coordinates to center and scale.
    adapted from https://github.com/Microsoft/human-pose-estimation.pytorch
    """
    pixel_std = 1
    center = np.zeros((2), dtype=np.float32)
    center[0] = x + w * 0.5
    center[1] = y + h * 0.5

    if w > aspect_ratio * h:
        h = w / aspect_ratio
    elif w < aspect_ratio * h:
        w = h * aspect_ratio

    scale = np.array( [w * 1.0 / pixel_std, h * 1.0 / pixel_std], dtype=np.float32)

    if center[0] != -1:
        scale = scale * scale_mult
    return center, scale


def test_transform(src, bbox):
    _aspect_ratio = float(src.shape[1]) / src.shape[0]
    xmin, ymin, xmax, ymax = bbox
    center, scale = _box_to_center_scale( xmin, ymin, xmax - xmin, ymax - ymin, _aspect_ratio)
    scale = scale * 1.0

    inp_h, inp_w = INPUT_SIZE

    trans = get_affine_transform(center, scale, 0, [inp_w, inp_h])
    img = cv2.warpAffine(src, trans, (int(inp_w), int(inp_h)), flags=cv2.INTER_LINEAR)
    bbox = _center_scale_to_box(center, scale)

    img = im_to_torch(img)
    img[0].add_(-0.406)
    img[1].add_(-0.457)
    img[2].add_(-0.480)

    return img, bbox


def heatmap_to_coord_simple(hms, bbox, hms_flip=None, **kwargs):
    if hms_flip is not None:
        hms = (hms + hms_flip) / 2
    if not isinstance(hms,np.ndarray):
        hms = hms.cpu().data.numpy()
    coords, maxvals = get_max_pred(hms)

    hm_h = hms.shape[1]
    hm_w = hms.shape[2]

    # post-processing
    for p in range(coords.shape[0]):
        hm = hms[p]
        px = int(round(float(coords[p][0])))
        py = int(round(float(coords[p][1])))
        if 1 < px < hm_w - 1 and 1 < py < hm_h - 1:
            diff = np.array((hm[py][px + 1] - hm[py][px - 1],
                             hm[py + 1][px] - hm[py - 1][px]))
            coords[p] += np.sign(diff) * .25

    preds = np.zeros_like(coords)

    # transform bbox to scale
    xmin, ymin, xmax, ymax = bbox
    w = xmax - xmin
    h = ymax - ymin
    center = np.array([xmin + w * 0.5, ymin + h * 0.5])
    scale = np.array([w, h])
    # Transform back
    for i in range(coords.shape[0]):
        preds[i] = transform_preds(coords[i], center, scale,
                                   [hm_w, hm_h])

    return preds, maxvals


def get_max_pred(heatmaps):
    num_joints = heatmaps.shape[0]
    width = heatmaps.shape[2]
    heatmaps_reshaped = heatmaps.reshape((num_joints, -1))
    idx = np.argmax(heatmaps_reshaped, 1)
    maxvals = np.max(heatmaps_reshaped, 1)

    maxvals = maxvals.reshape((num_joints, 1))
    idx = idx.reshape((num_joints, 1))

    preds = np.tile(idx, (1, 2)).astype(np.float32)

    preds[:, 0] = (preds[:, 0]) % width
    preds[:, 1] = np.floor((preds[:, 1]) / width)

    pred_mask = np.tile(np.greater(maxvals, 0.0), (1, 2))
    pred_mask = pred_mask.astype(np.float32)

    preds *= pred_mask
    return preds, maxvals


def transform_preds(coords, center, scale, output_size):
    target_coords = np.zeros(coords.shape)
    trans = get_affine_transform(center, scale, 0, output_size, inv=1)
    target_coords[0:2] = affine_transform(coords[0:2], trans)
    return target_coords


def affine_transform(pt, t):
    new_pt = np.array([pt[0], pt[1], 1.]).T
    new_pt = np.dot(t, new_pt)
    return new_pt[:2]
