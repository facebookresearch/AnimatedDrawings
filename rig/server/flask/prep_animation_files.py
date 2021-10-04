from PIL import Image, ImageDraw
import os, sys, shutil
from resources.exemplar_sketch import sketch as exemplar_sketch
from copy import deepcopy
from pathlib import Path
import numpy as np
import json
import yaml


def prep_animation_files(input_parent_dir, video_share_root):
    img_loc = Path(os.path.join(input_parent_dir, 'cropped_image.png'))
    assert img_loc.exists(),  "Image not found: {}".format(str(img_loc))

    mask_loc = Path(os.path.join(input_parent_dir, 'mask.png'))
    assert mask_loc.exists(), "Mask not found: {mask_loc}".format(str(mask_loc))

    keypoint_json_loc = Path(os.path.join(input_parent_dir, 'joint_locations.json'))
    assert keypoint_json_loc.exists(), "AP predictions not found: {}".format(str(keypoint_json_loc))

    outdir = os.path.join(input_parent_dir, 'animation')
    if os.path.exists(outdir): # delete old animation files if they exist
        shutil.rmtree(outdir)
    Path(outdir).mkdir(exist_ok=True, parents=True)

    uuid = input_parent_dir.split('/')[-1]
    video_dir = os.path.join(video_share_root, uuid)
    if os.path.exists(video_dir): # delete old video files if they exist
        shutil.rmtree(video_dir)


    img = Image.open(img_loc)
    im_size = max(img.size)
    img = img.convert('RGBA')
    square_img = Image.new( 'RGBA', (im_size, im_size), (255, 255, 255, 255))
    square_img.paste(img, (0, 0))
    square_img_loc = Path(os.path.join(outdir, Path(img_loc).name))
    square_img.save(str(square_img_loc))

    # open mask, make entire border 1px black to ensure contours cover whole character
    mask = Image.open(mask_loc).convert('RGB')
    mask_np = np.array(mask)
    mask_np[:, 0] = (0, 0, 0)
    mask_np[:, -1] = (0, 0, 0)
    mask_np[0, :] = (0, 0, 0)
    mask_np[-1, :] = (0, 0, 0)
    mask = Image.fromarray(mask_np)

    square_mask = Image.new('RGB', (im_size, im_size), (0, 0, 0))
    square_mask.paste(mask, (0, 0))
    square_mask.save(str(square_img_loc)[:-4] + '_mask.png')

    sketch = deepcopy(exemplar_sketch)

    sketch['image_name'] = img_loc.name
    #sketch['image_loc'] = str(square_img_loc.resolve())
    sketch['image_loc'] = None
    sketch['sketch_dim'] = square_img.size[0]

    with open(keypoint_json_loc, 'r') as f:
        keypoints = json.load(f)
    joints = {key: [val['x'], val['y']] for (key, val) in keypoints.items()}

    # slightly different naming convention used in animation code. switch these names.
    joints['head'] = joints.pop('nose')
    joints['left_hand'] = joints.pop('left_wrist')
    joints['right_hand'] = joints.pop('right_wrist')
    joints['left_foot'] = joints.pop('left_ankle')
    joints['right_foot'] = joints.pop('right_ankle')

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

    with open(os.path.join(outdir, f'{img_loc.stem}.yaml'), 'w') as f:
        yaml.dump(sketch, f)

    draw = ImageDraw.Draw(mask)
    for name, xy in joints.items():  # output image with joint locations on it for debugging purposes
        x, y = xy
        draw.ellipse((x-3, y-3, x+3, y+3), fill=(255, 0, 0), outline=(255, 255, 255))
    mask.save(os.path.join(outdir, f'{img_loc.stem}_mask_joints.png'))



if __name__ == '__main__':
    input_parent_dir = sys.argv[1]

    prep_animation_files(input_parent_dir)
