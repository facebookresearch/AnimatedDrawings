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

    outdir = './opengl_dev/sketch_animate/Data/Texture'
    Path(outdir).mkdir(exist_ok=True, parents=True)

    img = Image.open(img_loc)
    
    im_size = max(img.size)

    img = img.convert('RGBA')
    square_img = Image.new( 'RGBA', (im_size, im_size), (255, 255, 255, 255))
    square_img.paste(img, (0, 0))
    square_img.save(os.path.join(outdir, Path(img_name).name))

    mask = Image.open(mask_loc).convert('RGB')

    # make entire border 1px black to ensure contours cover whole character
    mask_np = np.array(mask)
    mask_np[:, 0] = (0, 0, 0)
    mask_np[:, -1] = (0, 0, 0)
    mask_np[0, :] = (0, 0, 0)
    mask_np[-1, :] = (0, 0, 0)
    
    mask = Image.fromarray(mask_np)
    square_mask = Image.new( 'RGB', (im_size, im_size), (0, 0, 0))
    square_mask.paste(mask, (0, 0))
    
    square_mask.save(os.path.join(outdir, Path(img_name).name[:-4] + '_mask.png'))

    sketch = deepcopy(exemplar_sketch)

    sketch['img_name'] = img_name
    sketch['image_loc'] = '../Data/Texture/{}'.format(img_name)

    sketch['sketch_dim'] = square_img.size[0]

    # get joint locations
    # TODO Update this and get list of joint names out
    joints ={}
    with open(os.path.join(anno_loc), 'r') as f:
        annos = json.load(f)
        for anno in annos:
            if anno['image_id'] == img_name:
                break
        assert anno['image_id'] == img_name

        ktr = iter(anno['keypoints'])
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
        #f.write('sketch='+sketch.__str__())

    draw = ImageDraw.Draw(mask)
    for name, xy in joints.items():  # output image with joint locations on it for debugging purposes
        x, y = xy
        draw.ellipse((x-3, y-3, x+3, y+3), fill=(255, 0, 0), outline=(255, 255, 255))
    mask.save(os.path.join(outdir, img_name[:-4] + '_mask_joints.png'))

    # create the yaml file to render this character with
    #with open('./opengl_dev/sketch_animate/sketch_animate/config/example_render.yaml', 'r') as f:
    with open('./opengl_dev/sketch_animate/sketch_animate/config/example_Running_Jump_4x_mixamo_render.yaml', 'r') as f:
    #with open('./opengl_dev/sketch_animate/sketch_animate/config/example_mixamo_hip_hop_dancing.yaml', 'r') as f:
    #with open('./opengl_dev/sketch_animate/sketch_animate/config/example_render_wave.yaml', 'r') as f:
        y = yaml.load(f)
    y['character_config'] = f'../Data/Texture/{img_name[:-4]}.yaml'

    with open(f'./opengl_dev/sketch_animate/sketch_animate/config/render_{img_name[:-4]}.yaml', 'w') as f:
        yaml.dump(y, f)



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
    img_name = sys.argv[1]

    img_loc = f'/private/home/hjessmith/flask/input_parent_dir/cropped_detections/color/{img_name}'
    assert os.path.exists(img_loc), "Image not found: {}".format(img_loc)

    mask_loc = f'/private/home/hjessmith/flask/input_parent_dir/cropped_detections/mask/{img_name}'
    assert os.path.exists(mask_loc), "Mask not found: {mask_loc}".format(mask_loc)

    anno_loc = f'/private/home/hjessmith/flask/input_parent_dir/cropped_detections/alpha_pose_out/alphapose-results.json'
    assert os.path.exists(anno_loc), "AP predictions not found: {}".format(anno_loc)

    main(img_name, anno_loc)
