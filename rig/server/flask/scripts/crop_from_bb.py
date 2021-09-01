import sys
sys.path.insert(0, '/private/home/hjessmith/utils_j')
import os
import json
import detectron2
import d2prediction_utils as d2p
import image_utils
import alphapose_utils
from PIL import Image, ImageFilter
from pathlib import Path

input_parent_dir = sys.argv[1]
img_loc = os.path.join(input_parent_dir, 'image.png')
bb_json_loc = os.path.join(input_parent_dir, 'bb.json')
cropped_img_out_loc = os.path.join(input_parent_dir, 'cropped_image.png')
gray_blur_img_out_loc = os.path.join(input_parent_dir, 'gray_blur.png')
sketch_DET_loc = os.path.join(input_parent_dir, 'sketch-DET.json')

## Create cropped image
img = Image.open(img_loc)
padding = 25
with open(bb_json_loc, 'r') as f:
    bb = json.load(f)
x1 = max(0, bb['x1'] - padding)
y1 = max(0, bb['y1'] - padding)
x2 = min(img.size[0], bb['x2']+padding)
y2 = min(img.size[1], bb['y2']+padding)

cropped_img = img.crop((x1, y1, x2, y2))
cropped_img.thumbnail((400, 400))
cropped_img.save(cropped_img_out_loc)

## Create gray blurred version of image for input to pose detector
cropped_img.convert('L').filter(ImageFilter.GaussianBlur(radius=2)).save(gray_blur_img_out_loc)
#Image.open(input_fn).convert('L').filter(ImageFilter.GaussianBlur(radius=2)).save(gray_blur_out_loc)

## Create sketch-DET.json for input to pose detector
w, h = cropped_img.size
cx, cy = int(w/2), int(h/2)
det = [{
        'category_id':1,
        'score':0.9,
        'bbox': (cx, cy, w, h),
        'image_id': gray_blur_img_out_loc,
}]
with open(sketch_DET_loc, 'w') as f:
        json.dump(det, f)

