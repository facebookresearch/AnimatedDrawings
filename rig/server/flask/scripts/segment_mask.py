import json
import os
from pathlib import Path
import sys
sys.path.insert(0, '/home/model-server/rig/server/utils')
import coco_utils
import image_utils
import numpy as np
from skimage import measure
from scipy.spatial import ConvexHull
from scipy import ndimage
from PIL import Image
import cv2
from matplotlib import pyplot as plt

orig_fn = os.path.join(sys.argv[1], 'cropped_image.png')
mask_output_loc = os.path.join(sys.argv[1], 'mask.png')
composite_output_loc = os.path.join(sys.argv[1], 'composite_mask.png')  

imgs = []

im_in = cv2.imread(orig_fn, cv2.IMREAD_GRAYSCALE)
c = cv2.imread(orig_fn, cv2.IMREAD_UNCHANGED)
r, g, b = c[:,:,0], c[:, :, 1], c[:, :, 2]
im_in = (np.min([r,g,b], axis=0))

img1 = Image.fromarray(np.array(Image.open(orig_fn)))

imgs.append(img1)

plt.rcParams['figure.figsize'] = [10, 10]

th3 = cv2.adaptiveThreshold(im_in,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,115,8)
th3 = cv2.bitwise_not(th3)
img3 = Image.fromarray(th3)
imgs.append(img3)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
opening = cv2.morphologyEx(th3, cv2.MORPH_CLOSE, kernel, iterations=1)
imgs.append(Image.fromarray(opening.copy()))
opening = cv2.morphologyEx(opening, cv2.MORPH_DILATE, kernel, iterations=1)
imgs.append(Image.fromarray(opening.copy()))

# Mask used to flood filling.
im_floodfill = opening.copy()
h, w = opening.shape[:2]

im_floodfill[:,0] = 255  
im_floodfill[:,w-1] = 255  
im_floodfill[0, :] = 255  
im_floodfill[h-1,:] = 255  

mask = np.zeros((h+2, w+2), np.uint8)
mask.fill(0)
mask = np.zeros((h+2, w+2), np.uint8)
mask.fill(0)

mask = np.zeros([opening.shape[0]+2, opening.shape[1]+2], np.uint8) 
mask[1:-1,1:-1] = opening.copy()

im_floodfill = np.empty(opening.shape, np.uint8)
im_floodfill.fill(255)

imgs.append(Image.fromarray(im_floodfill.copy()))

for x in range(0, w-1, 10):
    cv2.floodFill(im_floodfill, mask, (x, 0), 0);
    cv2.floodFill(im_floodfill, mask, (x, h-1), 0);
for y in range(0, h-1, 10):
    cv2.floodFill(im_floodfill, mask, (0, y), 0);
    cv2.floodFill(im_floodfill, mask, (w-1, y), 0);
    
imgs.append(Image.fromarray(im_floodfill.copy()))

mask2 = np.zeros([im_floodfill.shape[0]+2, im_floodfill.shape[1]+2], np.uint8) 
mask2[1:-1,1:-1] = im_floodfill.copy()
mask2 = cv2.bitwise_not(mask2)

# find contours in the image, and select the largest one
mask_contour = None
mask = None
biggest = 0
contours = measure.find_contours(mask2, 0.5)
for idx, c in enumerate(contours):
    x = np.zeros(mask2.T.shape, np.uint8)
    cv2.fillPoly(x, [np.int32(c)], 1)
    size = len(np.where(x == 1)[0])
    if size > biggest:
        mask_contour = x
        mask = x
        biggest = size

mask = ndimage.binary_fill_holes(mask).astype(int)
mask = 255 * mask.astype(np.uint8)
im_floodfill2 = mask.T[1:-1, 1:-1]  # so code names below match

imgs.append(Image.fromarray(im_floodfill2.copy()))

kernel = np.ones((5,5),np.uint8)
erosion = cv2.erode(im_floodfill2,kernel,iterations = 1)
_, dist_indices = ndimage.distance_transform_cdt(cv2.bitwise_not(erosion), return_indices=True)

img7 = cv2.bitwise_and(np.array(img1), np.array(img1), mask=im_floodfill2) 

Image.fromarray(im_floodfill2).save(mask_output_loc)
image_utils.get_image_composite(imgs, len(imgs)).save(composite_output_loc)
