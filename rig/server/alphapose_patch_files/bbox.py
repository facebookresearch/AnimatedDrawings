from __future__ import division

import torch
import numpy as np


def bbox_iou(bbox_a, bbox_b, offset=0):
    """Calculate Intersection-Over-Union(IOU) of two bounding boxes.

    Parameters
    ----------
    bbox_a : numpy.ndarray
        An ndarray with shape :math:`(N, 4)`.
    bbox_b : numpy.ndarray
        An ndarray with shape :math:`(M, 4)`.
    offset : float or int, default is 0
        The ``offset`` is used to control the whether the width(or height) is computed as
        (right - left + ``offset``).
        Note that the offset must be 0 for normalized bboxes, whose ranges are in ``[0, 1]``.

    Returns
    -------
    numpy.ndarray
        An ndarray with shape :math:`(N, M)` indicates IOU between each pairs of
        bounding boxes in `bbox_a` and `bbox_b`.

    """
    if bbox_a.shape[1] < 4 or bbox_b.shape[1] < 4:
        raise IndexError("Bounding boxes axis 1 must have at least length 4")

    tl = np.maximum(bbox_a[:, None, :2], bbox_b[:, :2])
    br = np.minimum(bbox_a[:, None, 2:4], bbox_b[:, 2:4])

    area_i = np.prod(br - tl + offset, axis=2) * (tl < br).all(axis=2)
    area_a = np.prod(bbox_a[:, 2:4] - bbox_a[:, :2] + offset, axis=1)
    area_b = np.prod(bbox_b[:, 2:4] - bbox_b[:, :2] + offset, axis=1)
    return area_i / (area_a[:, None] + area_b - area_i)


def bbox_xywh_to_xyxy(xywh):
    """Convert bounding boxes from format (x, y, w, h) to (xmin, ymin, xmax, ymax)

    Parameters
    ----------
    xywh : list, tuple or numpy.ndarray
        The bbox in format (x, y, w, h).
        If numpy.ndarray is provided, we expect multiple bounding boxes with
        shape `(N, 4)`.

    Returns
    -------
    tuple or numpy.ndarray
        The converted bboxes in format (xmin, ymin, xmax, ymax).
        If input is numpy.ndarray, return is numpy.ndarray correspondingly.

    """
    if isinstance(xywh, (tuple, list)):
        if not len(xywh) == 4:
            raise IndexError(
                "Bounding boxes must have 4 elements, given {}".format(len(xywh)))
        w, h = np.maximum(xywh[2] - 1, 0), np.maximum(xywh[3] - 1, 0)
        return (xywh[0], xywh[1], xywh[0] + w, xywh[1] + h)
    elif isinstance(xywh, np.ndarray):
        if not xywh.size % 4 == 0:
            raise IndexError(
                "Bounding boxes must have n * 4 elements, given {}".format(xywh.shape))
        xyxy = np.hstack((xywh[:, :2], xywh[:, :2] + np.maximum(0, xywh[:, 2:4] - 1)))
        return xyxy
    else:
        raise TypeError(
            'Expect input xywh a list, tuple or numpy.ndarray, given {}'.format(type(xywh)))


def bbox_xyxy_to_xywh(xyxy):
    """Convert bounding boxes from format (xmin, ymin, xmax, ymax) to (x, y, w, h).

    Parameters
    ----------
    xyxy : list, tuple or numpy.ndarray
        The bbox in format (xmin, ymin, xmax, ymax).
        If numpy.ndarray is provided, we expect multiple bounding boxes with
        shape `(N, 4)`.

    Returns
    -------
    tuple or numpy.ndarray
        The converted bboxes in format (x, y, w, h).
        If input is numpy.ndarray, return is numpy.ndarray correspondingly.

    """
    if isinstance(xyxy, (tuple, list)):
        if not len(xyxy) == 4:
            raise IndexError(
                "Bounding boxes must have 4 elements, given {}".format(len(xyxy)))
        x1, y1 = xyxy[0], xyxy[1]
        w, h = xyxy[2] - x1 + 1, xyxy[3] - y1 + 1
        return (x1, y1, w, h)
    elif isinstance(xyxy, np.ndarray):
        if not xyxy.size % 4 == 0:
            raise IndexError(
                "Bounding boxes must have n * 4 elements, given {}".format(xyxy.shape))
        return np.hstack((xyxy[:, :2], xyxy[:, 2:4] - xyxy[:, :2] + 1))
    else:
        raise TypeError(
            'Expect input xywh a list, tuple or numpy.ndarray, given {}'.format(type(xyxy)))


def bbox_clip_xyxy(xyxy, width, height):
    """Clip bounding box with format (xmin, ymin, xmax, ymax) to specified boundary.

    All bounding boxes will be clipped to the new region `(0, 0, width, height)`.

    Parameters
    ----------
    xyxy : list, tuple or numpy.ndarray
        The bbox in format (xmin, ymin, xmax, ymax).
        If numpy.ndarray is provided, we expect multiple bounding boxes with
        shape `(N, 4)`.
    width : int or float
        Boundary width.
    height : int or float
        Boundary height.

    Returns
    -------
    type
        Description of returned object.

    """
    if isinstance(xyxy, (tuple, list)):
        if not len(xyxy) == 4:
            raise IndexError(
                "Bounding boxes must have 4 elements, given {}".format(len(xyxy)))
        x1 = np.minimum(width - 1, np.maximum(0, xyxy[0]))
        y1 = np.minimum(height - 1, np.maximum(0, xyxy[1]))
        x2 = np.minimum(width - 1, np.maximum(0, xyxy[2]))
        y2 = np.minimum(height - 1, np.maximum(0, xyxy[3]))
        return (x1, y1, x2, y2)
    elif isinstance(xyxy, np.ndarray):
        if not xyxy.size % 4 == 0:
            raise IndexError(
                "Bounding boxes must have n * 4 elements, given {}".format(xyxy.shape))
        x1 = np.minimum(width - 1, np.maximum(0, xyxy[:, 0]))
        y1 = np.minimum(height - 1, np.maximum(0, xyxy[:, 1]))
        x2 = np.minimum(width - 1, np.maximum(0, xyxy[:, 2]))
        y2 = np.minimum(height - 1, np.maximum(0, xyxy[:, 3]))
        return np.hstack((x1, y1, x2, y2))
    else:
        raise TypeError(
            'Expect input xywh a list, tuple or numpy.ndarray, given {}'.format(type(xyxy)))


def transformBox(pt, bbox, input_size, output_size):
    inpH, inpW = input_size
    resH, _ = output_size

    center = torch.zeros(2)
    center[0] = (bbox[2] - 1 - bbox[0]) / 2
    center[1] = (bbox[3] - 1 - bbox[1]) / 2

    lenH = max(bbox[3] - bbox[1], (bbox[2] - bbox[0]) * inpH / inpW)
    lenW = lenH * inpW / inpH

    _pt = torch.zeros(2)
    _pt[0] = pt[0] - bbox[0]
    _pt[1] = pt[1] - bbox[1]
    # Move to center
    _pt[0] = _pt[0] + max(0, (lenW - 1) / 2 - center[0])
    _pt[1] = _pt[1] + max(0, (lenH - 1) / 2 - center[1])
    pt = (_pt * resH) / lenH
    pt[0] = round(float(pt[0]))
    pt[1] = round(float(pt[1]))
    return pt.int()


def transformBoxInvert(pt, bbox, resH, resW):
    center = torch.zeros(2)
    center[0] = (bbox[2] - 1 - bbox[0]) / 2
    center[1] = (bbox[3] - 1 - bbox[1]) / 2

    lenH = max(bbox[3] - bbox[1], (bbox[2] - bbox[0]) * resH / resW)
    lenW = lenH * resW / resH

    _pt = (pt * lenH) / resH

    if bool(((lenW - 1) / 2 - center[0]) > 0):
        _pt[0] = _pt[0] - ((lenW - 1) / 2 - center[0]).item()
    if bool(((lenH - 1) / 2 - center[1]) > 0):
        _pt[1] = _pt[1] - ((lenH - 1) / 2 - center[1]).item()

    new_point = torch.zeros(2)
    new_point[0] = _pt[0] + bbox[0]
    new_point[1] = _pt[1] + bbox[1]
    return new_point


def _box_to_center_scale(x, y, w, h, aspect_ratio=1.0, scale_mult=1.25):
    """Convert box coordinates to center and scale.
    adapted from https://github.com/Microsoft/human-pose-estimation.pytorch
    """
    pixel_std = 1
    center = np.zeros((2), dtype=np.float32)
    center[0] = x + w * 0.5
    center[1] = y + h * 0.5
    w = np.array(w)  # patch added to avoid floating point exception when dividing tensor by float
    h = np.array(h)  # patch added to avoid floating point exception when dividing tensor by float

    if w > aspect_ratio * h:
        h = w / aspect_ratio
    elif w < aspect_ratio * h:
        w = h * aspect_ratio
    scale = np.array(
        [w * 1.0 / pixel_std, h * 1.0 / pixel_std], dtype=np.float32)
    if center[0] != -1:
        scale = scale * scale_mult
    return center, scale


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


def _clip_aspect_ratio(boxes, aspect_ratio=1.0):
    xmin, ymin = boxes[:, 0], boxes[:, 1]
    xmax, ymax = boxes[:, 2], boxes[:, 3]

    w = xmax - xmin
    h = ymax - ymin

    c_x = xmin + w * 0.5
    c_y = ymin + h * 0.5

    idx = w > (aspect_ratio * h)
    h[idx] = w[idx] / aspect_ratio

    idx = w < (aspect_ratio * h)
    w[idx] = h[idx] * aspect_ratio

    new_boxes = torch.zeros(boxes.shape[0], 5)
    new_boxes[:, 1] = c_x - w * 0.5
    new_boxes[:, 2] = c_y - h * 0.5
    new_boxes[:, 3] = c_x + w * 0.5
    new_boxes[:, 4] = c_y + h * 0.5

    return new_boxes
