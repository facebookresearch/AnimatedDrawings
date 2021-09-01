import detectron2
from PIL import Image

def crop_from_multiple_bbs(img_path, d2_preds, padding=0):
	if len(d2_preds) == 0:
		return None
	img = Image.open(img_path)

        # create a bounding box encompassing all d2 prediction bounding boxes
	x1, y1, x2, y2 = img.size[0], img.size[1], 0, 0
	for idx in range(len(d2_preds)):
		_x1, _y1, _x2, _y2 = list(map(int, d2_preds.pred_boxes.tensor[idx]))
		x1 = min(x1, _x1)
		y1 = min(y1, _y1)
		x2 = max(x2, _x2)
		y2 = max(y2, _y2)

	x1 = max(0, x1-padding)
	y1 = max(0, y1-padding)
	x2 = min(img.size[0], x2+padding)
	y2 = min(img.size[1], y2+padding)

	return img.crop((x1, y1, x2, y2))

def crop_from_d2_bbs(img_path, d2_preds, padding=0):
	img = Image.open(img_path)
	cropped_imgs = []
	for idx in range(len(d2_preds)):
		x1, y1, x2, y2 = list(map(int, d2_preds.pred_boxes.tensor[idx]))
		x1 = max(0, x1-padding)
		y1 = max(0, y1-padding)
		x2 = min(img.size[0], x2+padding)
		y2 = min(img.size[1], y2+padding)
		cropped_imgs.append(img.crop((x1, y1, x2, y2)))
	return cropped_imgs


def get_mask_from_d2pred(d2pred):
    if len(d2pred) != 1:
        assert False

    pred_mask = d2pred.pred_masks[0]

    return pred_mask #* 0.8  # for now, because predictions are true/false, just weight true to 0.6

def get_bb_from_multiple_bb(d2_preds, padding=0):
	if len(d2_preds) == 0:
		return None

        # create a bounding box encompassing all d2 prediction bounding boxes
	x1, y1, x2, y2 = 999999, 999999, 0, 0
	for idx in range(len(d2_preds)):
		_x1, _y1, _x2, _y2 = list(map(int, d2_preds.pred_boxes.tensor[idx]))
		x1 = min(x1, _x1)
		y1 = min(y1, _y1)
		x2 = max(x2, _x2)
		y2 = max(y2, _y2)

	x1 = max(0, x1-padding)
	y1 = max(0, y1-padding)
	x2 = min(999999, x2+padding)
	y2 = min(999999, y2+padding)

	return {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}


def get_bb_from_d2pred(d2pred):
    if len(d2pred) != 1:
        assert False

    pred_box = d2pred.pred_boxes[0]

    return pred_box
