import math
import cv2
import munkres
import numpy as np
import torch


# solution proposed in https://github.com/pytorch/pytorch/issues/229#issuecomment-299424875 
def flip_tensor(tensor, dim=0):
    """
    flip the tensor on the dimension dim
    """
    inv_idx = torch.arange(tensor.shape[dim] - 1, -1, -1).to(tensor.device)
    return tensor.index_select(dim, inv_idx)


#
# derived from https://github.com/leoxiaobin/deep-high-resolution-net.pytorch
def flip_back(output_flipped, matched_parts):
    assert len(output_flipped.shape) == 4, 'output_flipped has to be [batch_size, num_joints, height, width]'

    output_flipped = flip_tensor(output_flipped, dim=-1)

    for pair in matched_parts:
        tmp = output_flipped[:, pair[0]].clone()
        output_flipped[:, pair[0]] = output_flipped[:, pair[1]]
        output_flipped[:, pair[1]] = tmp

    return output_flipped


def fliplr_joints(joints, joints_vis, width, matched_parts):
    # Flip horizontal
    joints[:, 0] = width - joints[:, 0] - 1

    # Change left-right parts
    for pair in matched_parts:
        joints[pair[0], :], joints[pair[1], :] = \
            joints[pair[1], :], joints[pair[0], :].copy()
        joints_vis[pair[0], :], joints_vis[pair[1], :] = \
            joints_vis[pair[1], :], joints_vis[pair[0], :].copy()

    return joints * joints_vis, joints_vis


def get_affine_transform(center, scale, pixel_std, rot, output_size, shift=np.array([0, 0], dtype=np.float32), inv=0):
    if not isinstance(scale, np.ndarray) and not isinstance(scale, list):
        print(scale)
        scale = np.array([scale, scale])

    scale_tmp = scale * 1.0 * pixel_std  # It was scale_tmp = scale * 200.0
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


def affine_transform(pt, t):
    new_pt = np.array([pt[0], pt[1], 1.]).T
    new_pt = np.dot(t, new_pt)
    return new_pt[:2]


def get_3rd_point(a, b):
    direct = a - b
    return b + np.array([-direct[1], direct[0]], dtype=np.float32)


def get_dir(src_point, rot_rad):
    sn, cs = np.sin(rot_rad), np.cos(rot_rad)

    src_result = [0, 0]
    src_result[0] = src_point[0] * cs - src_point[1] * sn
    src_result[1] = src_point[0] * sn + src_point[1] * cs

    return src_result
