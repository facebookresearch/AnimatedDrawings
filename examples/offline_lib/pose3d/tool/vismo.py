# This file is adoped from MotionBERT (https://github.com/Walter0807/MotionBERT/blob/main/lib/utils/vismo.py)
import numpy as np
import os
import cv2
import math
import copy
import imageio
import io
import torch
from tqdm import tqdm
from PIL import Image
import matplotlib
import matplotlib.pyplot as plt


def render_and_save(motion_input, save_path, keep_imgs=False, fps=25, color="#F96706#FB8D43#FDB381", with_conf=False,
                    draw_face=False):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    motion = copy.deepcopy(motion_input)
    if motion.shape[-1] == 2 or motion.shape[-1] == 3:
        motion = np.transpose(motion, (1, 2, 0))  # (T,17,D) -> (17,D,T)
    if motion.shape[1] == 2 or with_conf:
        colors = hex2rgb(color)
        if not with_conf:
            J, D, T = motion.shape
            motion_full = np.ones([J, 3, T])
            motion_full[:, :2, :] = motion
        else:
            motion_full = motion
        motion_full[:, :2, :] = pixel2world_vis_motion(motion_full[:, :2, :])
        motion2video(motion_full, save_path=save_path, colors=colors, fps=fps)
    else:
        motion_world = pixel2world_vis_motion(motion, dim=3)
        motion2video_3d(motion_world, save_path=save_path, keep_imgs=keep_imgs, fps=fps)


def pixel2world_vis(pose):
    #     pose: (17,2)
    return (pose + [1, 1]) * 512 / 2


def pixel2world_vis_motion(motion, dim=2, is_tensor=False):
    #     pose: (17,2,N)
    N = motion.shape[-1]
    if dim == 2:
        offset = np.ones([2, N]).astype(np.float32)
    else:
        offset = np.ones([3, N]).astype(np.float32)
        offset[2, :] = 0
    if is_tensor:
        offset = torch.tensor(offset)
    return (motion + offset) * 512 / 2


def get_img_from_fig(fig, dpi=120):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", pad_inches=0)
    buf.seek(0)
    img_arr = np.frombuffer(buf.getvalue(), dtype=np.uint8)
    buf.close()
    img = cv2.imdecode(img_arr, 1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
    return img


def rgb2rgba(color):
    return (color[0], color[1], color[2], 255)


def hex2rgb(hex, number_of_colors=3):
    h = hex
    rgb = []
    for i in range(number_of_colors):
        h = h.lstrip('#')
        hex_color = h[0:6]
        rgb_color = [int(hex_color[i:i + 2], 16) for i in (0, 2, 4)]
        rgb.append(rgb_color)
        h = h[6:]
    return rgb


def joints2image(joints_position, colors, transparency=False, H=1000, W=1000, nr_joints=49, imtype=np.uint8,
                 grayscale=False, bg_color=(255, 255, 255)):
    #     joints_position: [17*2]
    nr_joints = joints_position.shape[0]

    if nr_joints == 49:  # full joints(49): basic(15) + eyes(2) + toes(2) + hands(30)
        limbSeq = [[0, 1], [1, 2], [1, 5], [1, 8], [2, 3], [3, 4], [5, 6], [6, 7], \
                   [8, 9], [8, 13], [9, 10], [10, 11], [11, 12], [13, 14], [14, 15], [15, 16],
                   ]  # [0, 17], [0, 18]] #ignore eyes

        L = rgb2rgba(colors[0]) if transparency else colors[0]
        M = rgb2rgba(colors[1]) if transparency else colors[1]
        R = rgb2rgba(colors[2]) if transparency else colors[2]

        colors_joints = [M, M, L, L, L, R, R,
                         R, M, L, L, L, L, R, R, R,
                         R, R, L] + [L] * 15 + [R] * 15

        colors_limbs = [M, L, R, M, L, L, R,
                        R, L, R, L, L, L, R, R, R,
                        R, R]
    elif nr_joints == 15:  # basic joints(15) + (eyes(2))
        limbSeq = [[0, 1], [1, 2], [1, 5], [1, 8], [2, 3], [3, 4], [5, 6], [6, 7],
                   [8, 9], [8, 12], [9, 10], [10, 11], [12, 13], [13, 14]]
        # [0, 15], [0, 16] two eyes are not drawn

        L = rgb2rgba(colors[0]) if transparency else colors[0]
        M = rgb2rgba(colors[1]) if transparency else colors[1]
        R = rgb2rgba(colors[2]) if transparency else colors[2]

        colors_joints = [M, M, L, L, L, R, R,
                         R, M, L, L, L, R, R, R]

        colors_limbs = [M, L, R, M, L, L, R,
                        R, L, R, L, L, R, R]
    elif nr_joints == 17:
        #                       H36M, 0: 'root',
        #                             1: 'rhip',
        #                             2: 'rkne',
        #                             3: 'rank',
        #                             4: 'lhip',
        #                             5: 'lkne',
        #                             6: 'lank',
        #                             7: 'belly',
        #                             8: 'neck',
        #                             9: 'nose',
        #                             10: 'head',
        #                             11: 'lsho',
        #                             12: 'lelb',
        #                             13: 'lwri',
        #                             14: 'rsho',
        #                             15: 'relb',
        #                             16: 'rwri'
        limbSeq = [[0, 1], [1, 2], [2, 3], [0, 4], [4, 5], [5, 6], [0, 7], [7, 8], [8, 9], [8, 11], [8, 14], [9, 10],
                   [11, 12], [12, 13], [14, 15], [15, 16]]

        L = rgb2rgba(colors[0]) if transparency else colors[0]
        M = rgb2rgba(colors[1]) if transparency else colors[1]
        R = rgb2rgba(colors[2]) if transparency else colors[2]

        colors_joints = [M, R, R, R, L, L, L, M, M, M, M, L, L, L, R, R, R]
        colors_limbs = [R, R, R, L, L, L, M, M, M, L, R, M, L, L, R, R]

    else:
        raise ValueError("Only support number of joints be 49 or 17 or 15")

    if transparency:
        canvas = np.zeros(shape=(H, W, 4))
    else:
        canvas = np.ones(shape=(H, W, 3)) * np.array(bg_color).reshape([1, 1, 3])
    hips = joints_position[0]
    neck = joints_position[8]
    torso_length = ((hips[1] - neck[1]) ** 2 + (hips[0] - neck[0]) ** 2) ** 0.5
    head_radius = int(torso_length / 4.5)
    end_effectors_radius = int(torso_length / 15)
    end_effectors_radius = 7
    joints_radius = 7
    for i in range(0, len(colors_joints)):
        if i in (17, 18):
            continue
        elif i > 18:
            radius = 2
        else:
            radius = joints_radius
        if len(joints_position[i]) == 3:  # If there is confidence, weigh by confidence
            weight = joints_position[i][2]
            if weight == 0:
                continue
        cv2.circle(canvas, (int(joints_position[i][0]), int(joints_position[i][1])), radius, colors_joints[i],
                   thickness=-1)

    stickwidth = 2
    for i in range(len(limbSeq)):
        limb = limbSeq[i]
        cur_canvas = canvas.copy()
        point1_index = limb[0]
        point2_index = limb[1]
        point1 = joints_position[point1_index]
        point2 = joints_position[point2_index]
        if len(point1) == 3:  # If there is confidence, weigh by confidence
            limb_weight = min(point1[2], point2[2])
            if limb_weight == 0:
                bb = bounding_box(canvas)
                canvas_cropped = canvas[:, bb[2]:bb[3], :]
                continue
        X = [point1[1], point2[1]]
        Y = [point1[0], point2[0]]
        mX = np.mean(X)
        mY = np.mean(Y)
        length = ((X[0] - X[1]) ** 2 + (Y[0] - Y[1]) ** 2) ** 0.5
        alpha = math.degrees(math.atan2(X[0] - X[1], Y[0] - Y[1]))
        polygon = cv2.ellipse2Poly((int(mY), int(mX)), (int(length / 2), stickwidth), int(alpha), 0, 360, 1)
        cv2.fillConvexPoly(cur_canvas, polygon, colors_limbs[i])
        canvas = cv2.addWeighted(canvas, 0.4, cur_canvas, 0.6, 0)
        bb = bounding_box(canvas)
        canvas_cropped = canvas[:, bb[2]:bb[3], :]
    canvas = canvas.astype(imtype)
    canvas_cropped = canvas_cropped.astype(imtype)
    if grayscale:
        if transparency:
            canvas = cv2.cvtColor(canvas, cv2.COLOR_RGBA2GRAY)
            canvas_cropped = cv2.cvtColor(canvas_cropped, cv2.COLOR_RGBA2GRAY)
        else:
            canvas = cv2.cvtColor(canvas, cv2.COLOR_RGB2GRAY)
            canvas_cropped = cv2.cvtColor(canvas_cropped, cv2.COLOR_RGB2GRAY)
    return [canvas, canvas_cropped]


def motion2video(motion, save_path, colors, h=512, w=512, bg_color=(255, 255, 255), transparency=False, motion_tgt=None,
                 fps=25, save_frame=False, grayscale=False, show_progress=True, as_array=False):
    nr_joints = motion.shape[0]
    #     as_array = save_path.endswith(".npy")
    vlen = motion.shape[-1]

    out_array = np.zeros([vlen, h, w, 3]) if as_array else None
    videowriter = None if as_array else imageio.get_writer(save_path, fps=fps)

    if save_frame:
        frames_dir = save_path[:-4] + '-frames'
        ensure_dir(frames_dir)

    iterator = range(vlen)
    if show_progress: iterator = tqdm(iterator)
    for i in iterator:
        [img, img_cropped] = joints2image(motion[:, :, i], colors, transparency=transparency, bg_color=bg_color, H=h,
                                          W=w, nr_joints=nr_joints, grayscale=grayscale)
        if motion_tgt is not None:
            [img_tgt, img_tgt_cropped] = joints2image(motion_tgt[:, :, i], colors, transparency=transparency,
                                                      bg_color=bg_color, H=h, W=w, nr_joints=nr_joints,
                                                      grayscale=grayscale)
            img_ori = img.copy()
            img = cv2.addWeighted(img_tgt, 0.3, img_ori, 0.7, 0)
            img_cropped = cv2.addWeighted(img_tgt, 0.3, img_ori, 0.7, 0)
            bb = bounding_box(img_cropped)
            img_cropped = img_cropped[:, bb[2]:bb[3], :]
        if save_frame:
            save_image(img_cropped, os.path.join(frames_dir, "%04d.png" % i))
        if as_array:
            out_array[i] = img
        else:
            videowriter.append_data(img)

    if not as_array:
        videowriter.close()

    return out_array


def motion2video_3d(motion, save_path, fps=25, keep_imgs=False):
    #     motion: (17,3,N)
    videowriter = imageio.get_writer(save_path, fps=fps)
    vlen = motion.shape[-1]
    save_name = save_path.split('.')[0]
    frames = []
    joint_pairs = [[0, 1], [1, 2], [2, 3], [0, 4], [4, 5], [5, 6], [0, 7], [7, 8], [8, 9], [8, 11], [8, 14], [9, 10],
                   [11, 12], [12, 13], [14, 15], [15, 16]]
    joint_pairs_left = [[8, 11], [11, 12], [12, 13], [0, 4], [4, 5], [5, 6]]
    joint_pairs_right = [[8, 14], [14, 15], [15, 16], [0, 1], [1, 2], [2, 3]]

    color_mid = "#00457E"
    color_left = "#02315E"
    color_right = "#2F70AF"
    for f in tqdm(range(vlen)):
        j3d = motion[:, :, f]
        fig = plt.figure(0, figsize=(10, 10))
        ax = plt.axes(projection="3d")
        ax.set_xlim(-512, 0)
        ax.set_ylim(-256, 256)
        ax.set_zlim(-512, 0)
        # ax.set_xlabel('X')
        # ax.set_ylabel('Y')
        # ax.set_zlabel('Z')
        ax.view_init(elev=12., azim=80)
        plt.tick_params(left=False, right=False, labelleft=False,
                        labelbottom=False, bottom=False)
        for i in range(len(joint_pairs)):
            limb = joint_pairs[i]
            xs, ys, zs = [np.array([j3d[limb[0], j], j3d[limb[1], j]]) for j in range(3)]
            if joint_pairs[i] in joint_pairs_left:
                ax.plot(-xs, -zs, -ys, color=color_left, lw=3, marker='o', markerfacecolor='w', markersize=3,
                        markeredgewidth=2)  # axis transformation for visualization
            elif joint_pairs[i] in joint_pairs_right:
                ax.plot(-xs, -zs, -ys, color=color_right, lw=3, marker='o', markerfacecolor='w', markersize=3,
                        markeredgewidth=2)  # axis transformation for visualization
            else:
                ax.plot(-xs, -zs, -ys, color=color_mid, lw=3, marker='o', markerfacecolor='w', markersize=3,
                        markeredgewidth=2)  # axis transformation for visualization

        frame_vis = get_img_from_fig(fig)
        videowriter.append_data(frame_vis)
        plt.close()
    videowriter.close()


def save_image(image_numpy, image_path):
    image_pil = Image.fromarray(image_numpy)
    image_pil.save(image_path)


def bounding_box(img):
    a = np.where(img != 0)
    bbox = np.min(a[0]), np.max(a[0]), np.min(a[1]), np.max(a[1])
    return bbox


def convert_video2gif(src_video_path: str):
    video_reader = cv2.VideoCapture(src_video_path)
    fps = int(video_reader.get(cv2.CAP_PROP_FPS))
    frame_list = []
    print('Start Convert Gif!!')
    while True:
        ret, frame = video_reader.read()
        if ret is False:
            break

        # bgr -> rgb
        frame_list.append(frame[..., ::-1])

    output_save_path = os.path.join(os.path.dirname(src_video_path),
                                    os.path.basename(src_video_path).split('.')[0] + '.gif')

    imageio.mimsave(output_save_path, frame_list, 'GIF', duration=1 / fps * 1000, loop=0)
    print('Gif Has Convert Done!!')
