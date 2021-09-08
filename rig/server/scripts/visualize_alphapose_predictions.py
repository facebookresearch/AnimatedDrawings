from PIL import Image, ImageDraw, ImageFont
import os
import json
import numpy as np
import sys


results_fn = sys.argv[1]
out_dir = sys.argv[2]
confidence_fn = sys.argv[3]
img_dir = sys.argv[4]

from pathlib import Path
Path(out_dir).mkdir(exist_ok=True, parents=True)

with open(results_fn, 'r') as f:
    results = json.load(f)
confidences = []
skeleton = [[16, 14], [14, 12], [17, 15], [15, 13], [12, 13], [6, 12], [7, 13], [6, 7], [6, 8], [7, 9], [8, 10], [9, 11], [2, 3], [1, 2], [1, 3], [2, 4], [3, 5], [4, 6], [5, 7]]

keypoint_names= [
    ("nose", 0),
    ("left_eye", 0),
    ("right_eye", 0),
    ("left_ear", 0),
    ("right_ear", 0),
    ("left_shoulder", 1),
    ("right_shoulder", 1),
    ("left_elbow", 0.5),
    ("right_elbow", 0.5),
    ("left_wrist", 1),
    ("right_wrist", 1),
    ("left_hip", 1),
    ("right_hip",1),
    ("left_knee", 0.5),
    ("right_knee", 0.5),
    ("left_ankle", 1),
    ("right_ankle", 1)
]
from functools import reduce
kp_weight_sum = reduce((lambda a, b: a + b), [x[1] for x in keypoint_names])

f = open(confidence_fn, 'w')

for idx, result in enumerate(results):
    img = Image.open(os.path.join(img_dir, result['image_id'])).convert('RGB')
    draw = ImageDraw.Draw(img)
    jnts = []
    cs = []
    kt = iter(result['keypoints'])
    for jdx, xyc in enumerate(zip(kt, kt, kt)):
        x, y, c = xyc
        x = int(x)
        y = int(y)
        redval = int(255 * c)

        cs.append(c * keypoint_names[jdx][1])

        draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(redval, 0, 0), outline=(255, 0, 0))
        jnts.append([x, y, c])
    assert len(jnts) == 17
    for bone in skeleton:
        x1 = jnts[bone[0]-1][0]
        y1 = jnts[bone[0]-1][1]

        x2 = jnts[bone[1]-1][0]
        y2 = jnts[bone[1]-1][1]

        redval = int(255 * (jnts[bone[0]-1][2] + jnts[bone[0]-1][2]) / 2)

        draw.line((x1, y1, x2, y2), fill=(redval, 0, 0), width=2)

    font = ImageFont.truetype("/home/model-server/rig/server/fonts/VeraMono.ttf", 16)
    draw.text((0, 0), "Weighted Confidence: {:.2f}".format(np.sum(np.array(cs)/kp_weight_sum)), (255, 0, 255), font=font)

    f.write('{} {}\n'.format(result['image_id'], np.sum(np.array(cs)/kp_weight_sum)))



    img.save(os.path.join(out_dir, '{}').format(result['image_id']))
f.close()
x =2
