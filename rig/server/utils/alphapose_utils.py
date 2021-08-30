from PIL import Image, ImageDraw
import numpy as np
import os
import json

def make_DET_file(img_dir, output_file):
	def bbox1(img):
		w, h = img.size
		cx, cy = int(w/2), int(h/2)
		return cx, cy, w, h

	dets = []
	for img_name in os.listdir(img_dir):
		if not img_name.endswith('.png'):
			continue

		img_fn = os.path.abspath(os.path.join(img_dir, img_name))
		img = Image.open(img_fn)
		bbox = bbox1(img)

		det = {
			'category_id':1,
			'score':0.9,
			'bbox':bbox,
			'image_id': img_fn,
		}

		dets.append(det)

	with open(output_file, 'w') as f:
		json.dump(dets, f)


