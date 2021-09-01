import sys
sys.path.insert(0, '/private/home/hjessmith/utils_j')
import coco_utils as cu
from functools import reduce
from PIL import Image, ImageDraw, ImageFont
import os
import json
import numpy as np
import sys
from pathlib import Path


results_fn = sys.argv[1]
out_dir = sys.argv[2]
confidence_fn = sys.argv[3]

Path(out_dir).mkdir(exist_ok=True, parents=True)

with open(results_fn, 'r') as f:
    results = json.load(f)

confidences = []
skeleton = [ [x-1, y-1] for x,y in cu.bones]

keypoint_weights= {
    "nose": 0,
    "left_eye": 0,
    "right_eye": 0,
    "left_ear": 0,
    "right_ear": 0,
    "left_shoulder": 1,
    "right_shoulder": 1,
    "left_elbow": 0.5,
    "right_elbow": 0.5,
    "left_wrist": 1,
    "right_wrist": 1,
    "left_hip": 1,
    "right_hip":1,
    "left_knee": 0.5,
    "right_knee": 0.5,
    "left_ankle": 1,
    "right_ankle": 1
}

kp_weight_sum = reduce((lambda a, b: a + b), keypoint_weights.values())

f = open(confidence_fn, 'w')
f.write('{},{},{},{},{},{},{},{},{},{}\n'.format(
    'image name', 
    'weighted_confidence',
    'left_arm_mean_confidence',
    'left_arm_min_confidence',
    'right_arm_mean_confidence',
    'right_arm_min_confidence',
    'left_leg_mean_confidence',
    'left_leg_min_confidence',
    'right_leg_mean_confidence',
    'right_leg_min_confidence',
))

for idx, result in enumerate(results):
    img = Image.open(os.path.join(out_dir, 'cropped_image.png')).convert('RGB')
    draw = ImageDraw.Draw(img)

    jnts, cs = [], []
    kt = iter(result['keypoints'])
    for jdx, (x, y, c) in enumerate(zip(kt, kt, kt)):
        x, y, redval = int(x), int(y), int(255 * c)

        cs.append(keypoint_weights[cu.keypoint_names[jdx]] * c)

        draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(redval, 0, 0), outline=(255, 0, 0))
        jnts.append([x, y, c])

    assert len(jnts) == 17

    for bone in skeleton:
        x1 = jnts[bone[0]][0]
        y1 = jnts[bone[0]][1]

        x2 = jnts[bone[1]][0]
        y2 = jnts[bone[1]][1]

        redval = int(255 * (jnts[bone[0]][2] + jnts[bone[0]][2]) / 2)

        draw.line((x1, y1, x2, y2), fill=(redval, 0, 0), width=2)

    font = ImageFont.truetype("/private/home/hjessmith/font/Arial Unicode.ttf", 12)


    # write confidence values for image
    weighted_confidence = np.sum(np.array(cs)/kp_weight_sum)
    left_arm_mean_confidence = np.mean([jnts[cu.keypoint_names.index(name)][2]  for name in ('left_shoulder', 'left_elbow', 'left_wrist')])
    left_arm_min_confidence = np.min([jnts[cu.keypoint_names.index(name)][2]    for name in ('left_shoulder', 'left_elbow', 'left_wrist')])
    right_arm_mean_confidence = np.mean([jnts[cu.keypoint_names.index(name)][2] for name in ('right_shoulder', 'right_elbow', 'right_wrist')])
    right_arm_min_confidence = np.min([jnts[cu.keypoint_names.index(name)][2]   for name in ('right_shoulder', 'right_elbow', 'right_wrist')])

    left_leg_mean_confidence = np.mean([jnts[cu.keypoint_names.index(name)][2]  for name in ('left_hip', 'left_knee', 'left_ankle')])
    left_leg_min_confidence = np.min([jnts[cu.keypoint_names.index(name)][2]    for name in ('left_hip', 'left_knee', 'left_ankle')])
    right_leg_mean_confidence = np.mean([jnts[cu.keypoint_names.index(name)][2] for name in ('right_hip', 'right_knee', 'right_ankle')])
    right_leg_min_confidence = np.min([jnts[cu.keypoint_names.index(name)][2]   for name in ('right_hip', 'right_knee', 'right_ankle')])

    f.write('{},{},{},{},{},{},{},{},{},{}\n'.format(
        result['image_id'], 
        weighted_confidence,
        left_arm_mean_confidence,
        left_arm_min_confidence,
        right_arm_mean_confidence,
        right_arm_min_confidence,
        left_leg_mean_confidence,
        left_leg_min_confidence,
        right_leg_mean_confidence,
        right_leg_min_confidence,
))

    for idx, (name, score) in enumerate((
        ('conf', weighted_confidence),
        ('la_mean', left_arm_mean_confidence),
        ('la_min',  left_arm_min_confidence),
        ('ra_mean', right_arm_mean_confidence),
        ('ra_min',  right_arm_min_confidence),
        ('ll_mean', left_leg_mean_confidence),
        ('ll_min',  left_leg_min_confidence),
        ('rl_mean', right_leg_mean_confidence),
        ('rl_min',  right_leg_min_confidence)
    )):
        draw.text((0, 15*idx), "{}: {:.2f}".format(name, score), (255, 0, 255), font=font)
    img.save(os.path.join(out_dir, 'joint_overlay.png'))

f.close()
