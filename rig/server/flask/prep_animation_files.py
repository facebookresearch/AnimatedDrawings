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


UPLOAD_BUCKET = s3_object.s3_object('dev-demo-sketch-out-interim-files')


def prep_animation_files(unique_id, video_share_root):
    # jkimg_loc = Path(os.path.join(unique_id, 'cropped_image.png'))
    # jkassert img_loc.exists(),  "Image not found: {}".format(str(img_loc))

    # jkmask_loc = Path(os.path.join(unique_id, 'mask.png'))
    # jkassert mask_loc.exists(), "Mask not found: {mask_loc}".format(str(mask_loc))

    # jkkeypoint_json_loc = Path(os.path.join(unique_id, 'joint_locations.json'))
    # jkassert keypoint_json_loc.exists(), "AP predictions not found: {}".format(str(keypoint_json_loc))



    #img_loc = s3_object.get_object_bytes(unique_id, 'cropped_image.png')
    #mask_loc = s3_object.get_object_bytes(unique_id, 'mask.png')

    #keypoint_json_loc = s3_object.get_object_bytes(unique_id, 'joint_locations.json')

    #uuid = unique_id.split('/')[-1]
    #if uuid directory in video bucket exists, then delete
    #video_dir = os.path.join(video_share_root, uuid)
    #if os.path.exists(video_dir): # delete old video files if they exist
    #    shutil.rmtree(video_dir)

    assert UPLOAD_BUCKET.verify_object(unique_id, 'cropped_image.png') == True, f"Image not found: {unique_id}/cropped_image.png"
    img = UPLOAD_BUCKET.get_object_image_as_np(unique_id, "cropped_image.png")
    img = Image.fromarray(img)
    im_size = max(img.size)
    img = img.convert('RGBA')
    square_img = Image.new( 'RGBA', (im_size, im_size), (255, 255, 255, 255))
    # save square_img data as cropped_image.png and save it to s3
    square_img.paste(img, (0, 0))
    #UPLOAD_BUCKET.write_object(f"{unique_id}/animation", "cropped_image.png", square_img)
    UPLOAD_BUCKET.write_np_to_png_object(f"{unique_id}/animation", "cropped_image.png", np.array(square_img))

    # open mask, make entire border 1px black to ensure contours cover whole character
    assert UPLOAD_BUCKET.verify_object(unique_id, 'mask.png') == True, f"Image not found: {unique_id}/mask.png"
    mask = UPLOAD_BUCKET.get_object_image_as_np(unique_id, "mask.png")

    mask_np = np.array(mask)
    mask_np[:, 0] = (0, 0, 0)
    mask_np[:, -1] = (0, 0, 0)
    mask_np[0, :] = (0, 0, 0)
    mask_np[-1, :] = (0, 0, 0)
    mask = Image.fromarray(mask_np)

    square_mask = Image.new('RGB', (im_size, im_size), (0, 0, 0))
    square_mask.paste(mask, (0, 0))

    # save square_mask byte data as cropped_image_mask.png
    # UPLOAD_BUCKET.write_object(f"{unique_id}/animation", "cropped_image_mask.png", square_mask)
    UPLOAD_BUCKET.write_np_to_png_object(f"{unique_id}/animation", "cropped_image_mask.png", np.array(square_mask))

    sketch = deepcopy(exemplar_sketch)

    sketch['image_name'] = 'cropped_image.png'
    sketch['image_loc'] = None
    sketch['sketch_dim'] = square_img.size[0]

    # pull joint_locations.json object as bytes, save as keypoints
    assert UPLOAD_BUCKET.verify_object(unique_id, 'joint_locations.json') == True, f"json not found: {unique_id}/joint_location.json"
    keypoints = UPLOAD_BUCKET.get_object_bytes(unique_id, 'joint_locations.json')
    keypoints = json.loads(keypoints)

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

    #yaml_object = json.dumps(bb, indent = 4) 
    UPLOAD_BUCKET.write_object(f'{unique_id}/animation', "cropped_image.yaml", yaml.dump(sketch))

    draw = ImageDraw.Draw(mask)
    for name, xy in joints.items():  # output image with joint locations on it for debugging purposes
        x, y = xy
        draw.ellipse((x-3, y-3, x+3, y+3), fill=(255, 0, 0), outline=(255, 255, 255))

    #save s3 cropped_image_mask_joints.png using mask data
    UPLOAD_BUCKET.write_np_to_png_object(f'{unique_id}/animation', "cropped_image_mask_joints.png", np.array(mask))


# pretty sure this isnt needed, quick research
'''if __name__ == '__main__':
    #unique_id = sys.argv[1]

    prep_animation_files(unique_id)'''
