from PIL import Image, ImageDraw
import os, sys
from exemplar_sketch import sketch as exemplar_sketch
from copy import deepcopy
from pathlib import Path
import shutil
import numpy as np
import json
import yaml


def main(img_name, anno_loc):

    img = Image.open(os.path.join(img_loc, img_name))
    img = img.convert('RGBA')

    mask = Image.open(os.path.join(mask_loc, img_name))
    mask = mask.convert('RGB')
    
    # image must be square
    if img.size[0] != img.size[1]:
        size = max(img.size)
        _img= Image.new('RGBA', (size, size), color=(255, 255, 255, 255))
        _img.paste(img, (0, 0))
        img = _img
        
        _mask= Image.new('RGB', (size, size), color=(0, 0, 0))
        _mask.paste(mask, (0, 0))
        mask = _mask

    img.save(os.path.join(outdir, img_name))

    # make entire border 1px black to ensure contours cover whole character
    mask_np = np.array(mask)
    mask_np[:, 0] = (0, 0, 0)
    mask_np[:, -1] = (0, 0, 0)
    mask_np[0, :] = (0, 0, 0)
    mask_np[-1, :] = (0, 0, 0)
    mask = Image.fromarray(mask_np)
    mask.save(os.path.join(outdir, img_name[:-4] + '_mask.png'))

    sketch = deepcopy(exemplar_sketch)

    sketch['img_name'] = img_name
    sketch['image_loc'] = '../Data/Texture/{}'.format(img_name)

    sketch['sketch_dim'] = img.size[0]

    joints ={}
    with open(os.path.join(anno_loc), 'r') as f:
        annos = json.load(f)
        ktr = iter(annos[img_name])
        for idx, xyc in enumerate(zip(ktr, ktr, ktr)):
            name = keypoint_names[idx]
            x, y, c = xyc
            joints[name] = [int(x), int(y)]

    joints['root'] = [
        (joints['left_hip'][0] + joints['right_hip'][0]) / 2,
        (joints['left_hip'][1] + joints['right_hip'][1]) / 2
    ]
    joints['torso'] = [
        (joints['left_shoulder'][0] + joints['right_shoulder'][0]) / 2,
        (joints['left_shoulder'][1] + joints['right_shoulder'][1]) / 2
    ]
    joints['head'] = [
        joints['torso'][0],
        joints['head'][1]
    ]
    joints['neck'] = [
        joints['head'][0],
        (joints['head'][1] + joints['torso'][1]) / 2
    ]
    for item in sketch['skeleton']:
        item['loc'] = joints[item['name']]

    with open(os.path.join(outdir, img_name[:-4] +'.yaml'), 'w') as f:
        yaml.dump(sketch, f)

    draw = ImageDraw.Draw(mask)
    for name, xy in joints.items():  # visualize image with joint locations on it. useful for debugging
        x, y = xy
        draw.ellipse((x-3, y-3, x+3, y+3), fill=(255, 0, 0), outline=(255, 255, 255))
    mask.save(os.path.join(outdir, img_name[:-4] + '_mask_joints.png'))

keypoint_names= [
    "head",
    "left_eye",
    "right_eye",
    "left_ear",
    "right_ear",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_hand",
    "right_hand",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_foot",
    "right_foot"
]

if __name__ == '__main__':
    mask_loc = sys.argv[1]
    img_loc = sys.argv[2]
    anno_loc = sys.argv[3]
    outdir = sys.argv[4]
    Path(outdir).mkdir(exist_ok=True, parents=True)

    for img_name in os.listdir(img_loc):
        main(img_name, anno_loc)
