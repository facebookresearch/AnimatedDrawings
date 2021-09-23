import os
import sys
import numpy as np
from skimage import measure
from scipy import ndimage
import cv2


def threshold(im_in):
    im_out_r = cv2.adaptiveThreshold(im_in,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,115,8)
    im_out = cv2.bitwise_not(im_out_r)
    return im_out


def morph_ops(im_in):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    im_inter = cv2.morphologyEx(im_in, cv2.MORPH_CLOSE, kernel, iterations=1)
    im_out = cv2.morphologyEx(im_inter, cv2.MORPH_DILATE, kernel, iterations=1)
    return im_out

def flood_fill(im_in):
    im_floodfill = im_in.copy()
    h, w = im_in.shape[:2]

    im_floodfill[:,0] = 255
    im_floodfill[:,w-1] = 255
    im_floodfill[0, :] = 255
    im_floodfill[h-1,:] = 255

    mask = np.zeros((h+2, w+2), np.uint8)
    mask.fill(0)
    mask = np.zeros((h+2, w+2), np.uint8)
    mask.fill(0)

    mask = np.zeros([im_in.shape[0]+2, im_in.shape[1]+2], np.uint8)
    mask[1:-1,1:-1] = im_in.copy()

    im_floodfill = np.empty(im_in.shape, np.uint8)
    im_floodfill.fill(255)

    for x in range(0, w-1, 10):
        cv2.floodFill(im_floodfill, mask, (x, 0), 0);
        cv2.floodFill(im_floodfill, mask, (x, h-1), 0);
    for y in range(0, h-1, 10):
        cv2.floodFill(im_floodfill, mask, (0, y), 0);
        cv2.floodFill(im_floodfill, mask, (w-1, y), 0);

    mask2 = np.zeros([im_floodfill.shape[0]+2, im_floodfill.shape[1]+2], np.uint8)
    mask2[1:-1,1:-1] = im_floodfill.copy()
    mask2 = cv2.bitwise_not(mask2)

    return mask2

def retain_largest_contour(mask2):
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
    im_floodfill2 = mask.T[1:-1, 1:-1]

    return im_floodfill2
    #kernel = np.ones((5,5),np.uint8)
    #erosion = cv2.erode(im_floodfill2,kernel,iterations = 1)
    #_, dist_indices = ndimage.distance_transform_cdt(cv2.bitwise_not(erosion), return_indices=True)


def get_img_from_work_dir(work_dir):
    orig_fn = os.path.join(work_dir, 'cropped_image.png')

    c = cv2.imread(orig_fn, cv2.IMREAD_UNCHANGED)
    r, g, b = c[:,:,0], c[:, :, 1], c[:, :, 2]
    im_in = (np.min([r,g,b], axis=0))

    return im_in


def segment_mask(work_dir):
    im_in = get_img_from_work_dir(work_dir)

    th_img = threshold(im_in)

    mo_img = morph_ops(th_img)

    fl_img = flood_fill(mo_img)

    mask = retain_largest_contour(fl_img)

    cv2.imwrite(os.path.join(work_dir, 'mask.png'), mask)
