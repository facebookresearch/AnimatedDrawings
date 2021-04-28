import sys
sys.path.insert(0, 'utils')
import os
import pickle
import detectron2
import d2prediction_utils as d2p
import image_utils
import alphapose_utils
from PIL import Image
from pathlib import Path

img_dir = sys.argv[1]
d2_pred_dir = sys.argv[2]
out_dir = sys.argv[3]
gray_blur_out_dir = sys.argv[4]

Path(out_dir).mkdir(exist_ok=True, parents=True)
Path(gray_blur_out_dir).mkdir(exist_ok=True, parents=True)

for fn in [x for x in os.listdir(d2_pred_dir) if x.endswith('pickle')]:

	with open(os.path.join(d2_pred_dir, fn), 'rb') as f:
		d2_preds = pickle.load(f)

	cropped_img = d2p.crop_from_multiple_bbs(os.path.join(img_dir, fn.replace('pickle', 'png')), d2_preds, 25)
	if not cropped_img:
		continue

	out_loc = os.path.join(out_dir, '{}.png'.format(fn.split('.')[0]))
	cropped_img.thumbnail((400, 400))
	cropped_img.save(out_loc)

	gray_blur_out_loc = os.path.abspath(os.path.join(gray_blur_out_dir, '{}.png'.format(fn.split('.')[0])))
	image_utils.convert_grayscale_and_blur(out_loc, gray_blur_out_loc, 2)

sketch_dir_loc = os.path.abspath(gray_blur_out_dir+'/../'+'sketch-DET.json')
alphapose_utils.make_DET_file(gray_blur_out_dir, sketch_dir_loc)

