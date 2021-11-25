from re import S, U
from PIL import Image, ImageDraw
import os, sys, shutil
from resources.exemplar_sketch import sketch as exemplar_sketch
from copy import deepcopy
from pathlib import Path
import numpy as np
import json
import yaml
import s3_object


s3_object = s3_object.s3_object('dev-demo-sketch-out-interim-files')


def prep_animation_files(unique_id, video_share_root):
    img_loc = Path(os.path.join(unique_id, 'cropped_image.png'))
    assert img_loc.exists(),  "Image not found: {}".format(str(img_loc))

    mask_loc = Path(os.path.join(input_parent_dir, 'mask.png'))
    assert mask_loc.exists(), "Mask not found: {}".format(str(mask_loc))

    keypoint_json_loc = Path(os.path.join(unique_id, 'joint_locations.json'))
    assert keypoint_json_loc.exists(), "AP predictions not found: {}".format(str(keypoint_json_loc))

    img_loc = s3_object.get_object_bytes(unique_id, 'cropped_image.png')
    mask_loc = s3_object.get_object_bytes(unique_id, 'mask.png')
    keypoint_json_loc = s3_object.get_object_bytes(unique_id, 'joint_locations.json')
    
    assert s3_object.verify_object(unique_id, 'cropped_image.png') == True, "Image not found: {}".format(str(img_loc))
    assert s3_object.verify_object(unique_id, 'mask.png') == True, "Image not found: {}".format(str(img_loc))
    assert s3_object.verify_object(unique_id, 'joint_locations.json') == True, "Image not found: {}".format(str(img_loc))


    #uuid = unique_id.split('/')[-1]
    #if uuid directory in video bucket exists, then delete
    #video_dir = os.path.join(video_share_root, uuid)
    #if os.path.exists(video_dir): # delete old video files if they exist
    #    shutil.rmtree(video_dir)


    img = Image.open(img_loc)
    im_size = max(img.size)
    img = img.convert('RGBA')
    square_img = Image.new( 'RGBA', (im_size, im_size), (255, 255, 255, 255))
    # save square_img data as cropped_image.png and save it to s3
    square_img.paste(img, (0, 0))
    s3_object.write_object(unique_id, "cropped_image.png", square_img)

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

    # save square_mask byte data as cropped_image_mask.png
    s3_object.write_object(unique_id, "cropped_image_mask.png", square_mask)

    sketch = deepcopy(exemplar_sketch)

    sketch['image_name'] = img_loc.name
    #sketch['image_loc'] = str(square_img_loc.resolve())
    sketch['image_loc'] = None
    sketch['sketch_dim'] = square_img.size[0]

    # pull joint_locations.json object as bytes, save as keypoints
    keypoints = s3_object.get_object_bytes(unique_id, 'joint_locations.json')

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

    # save cropped_image.yaml using sketch byte data
    s3_object.write_object(unique_id, "cropped_image.yaml", sketch)

    draw = ImageDraw.Draw(mask)
    for name, xy in joints.items():  # output image with joint locations on it for debugging purposes
        x, y = xy
        draw.ellipse((x-3, y-3, x+3, y+3), fill=(255, 0, 0), outline=(255, 255, 255))

    #save s3 cropped_image_mask_joints.png using mask data
    s3_object.write_object(unique_id, "cropped_image_mask_joints.png", mask)


# pretty sure this isnt needed, quick research
'''if __name__ == '__main__':
    #unique_id = sys.argv[1]

    prep_animation_files(unique_id)'''
