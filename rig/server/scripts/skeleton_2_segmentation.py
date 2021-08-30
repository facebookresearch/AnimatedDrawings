import sys
sys.path.insert(0, 'utils')
import coco_utils
import image_utils

from PIL import Image
from skimage import measure
from scipy import ndimage
from scipy.spatial import ConvexHull

import numpy as np
import cv2
import json
import os
from pathlib import Path

alphapose_pred = sys.argv[1]  
imgs_dir = sys.argv[2]  
outdir = sys.argv[3]  

Path(outdir).mkdir(exist_ok=True, parents=True)

keypoints_dict = {}

with open(alphapose_pred, 'r') as f:
    ap_pred = json.load(f)
    
ap_pred_dict = {}
for each in ap_pred:
    ap_pred_dict[each['image_id']] = each

for img_fn in os.listdir(imgs_dir):
    orig_fn = os.path.join(imgs_dir, img_fn)

    # Open the original image
    im_in = cv2.imread(orig_fn, cv2.IMREAD_GRAYSCALE)
    c = cv2.imread(orig_fn, cv2.IMREAD_UNCHANGED)
    r, g, b = c[:,:,0], c[:, :, 1], c[:, :, 2]
    im_in = (np.min([r,g,b], axis=0))

    # Use adaptive thresholding to create a binary image
    binary_img = cv2.adaptiveThreshold(im_in,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,115,8)
    binary_img = cv2.bitwise_not(binary_img)

    # Use closing and dilating to clean the mask
    kernel3 = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    closed = cv2.morphologyEx(binary_img, cv2.MORPH_CLOSE, kernel3, iterations=1)
    opened = cv2.morphologyEx(closed, cv2.MORPH_DILATE, kernel3, iterations=1)

    # Floodfill from edges
    h, w = opened.shape[:2]
    mask1 = np.zeros([h+2, w+2], np.uint8) 
    mask1[1:-1,1:-1] = opened.copy()

    im_floodfill = np.empty(opened.shape, np.uint8)
    im_floodfill.fill(255)

    for x in range(0, w-1, 10):
        cv2.floodFill(im_floodfill, mask1, (x,   0), 0);
        cv2.floodFill(im_floodfill, mask1, (x, h-1), 0);
    for y in range(0, h-1, 10):
        cv2.floodFill(im_floodfill, mask1, (  0, y), 0);
        cv2.floodFill(im_floodfill, mask1, (w-1, y), 0);
        
    im_floodfill2 = np.zeros([im_floodfill.shape[0]+2, im_floodfill.shape[1]+2], np.uint8) 
    im_floodfill2[1:-1,1:-1] = im_floodfill.copy()
    im_floodfill2 = cv2.bitwise_not(im_floodfill2)
    
    # find and retain the largest contour after floodfilling
    mask2, biggest = None, 0
    contours = measure.find_contours(im_floodfill2, 0.5)
    for idx, c in enumerate(contours):
        x = np.zeros(im_floodfill2.T.shape, np.uint8)
        cv2.fillPoly(x, [np.int32(c)], 1)
        size = len(np.where(x == 1)[0])
        if size > biggest:
            mask2, biggest = x, size

    # fill holes
    mask3 = ndimage.binary_fill_holes(mask2).astype(int)
    mask3 = 255 * mask3.astype(np.uint8)

    # remove padding
    final_mask = mask3.T[1:-1, 1:-1]  

    # if any joints predicted by alphapose would fall outside of this mask, move them to the closest point within the mask
    _, dist_indices = ndimage.distance_transform_cdt(cv2.bitwise_not(final_mask), return_indices=True)
    
    _kpts = []
    for idx in range(17):
        x, y = ap_pred_dict[img_fn]['keypoints'][idx*3:idx*3 + 2]
        x, y = tuple(map(int, [x, y]))
        x = max(0, min(x, dist_indices.shape[2]-1))
        y = max(0, min(y, dist_indices.shape[1]-1))
        y, x = dist_indices[:, y, x]
        _kpts += [int(x), int(y), 2]

    keypoints_dict[img_fn] = _kpts

    Image.fromarray(final_mask).save(os.path.join(outdir, img_fn))

with open(os.path.join(outdir, '..', 'keypoints-postmask.json'), 'w') as f:
    json.dump(keypoints_dict, f)
