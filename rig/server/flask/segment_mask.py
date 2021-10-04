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
    # create mask that is 2 px taller and wider than im_in. make mask border = 0, paste image inside center
    mask = np.zeros([im_in.shape[0]+2, im_in.shape[1]+2], np.uint8)
    mask[1:-1,1:-1] = im_in.copy()

    # im_floodfill is results of floodfill. Starts off all white
    im_floodfill = np.full(im_in.shape, 255, np.uint8)

    # choose 10 points along each image side. use as seed for floodfill. flood while using mask
    h, w = im_in.shape[:2]
    for x in range(0, w-1, 10):
        cv2.floodFill(im_floodfill, mask, (x, 0), 0);
        cv2.floodFill(im_floodfill, mask, (x, h-1), 0);
    for y in range(0, h-1, 10):
        cv2.floodFill(im_floodfill, mask, (0, y), 0);
        cv2.floodFill(im_floodfill, mask, (w-1, y), 0);

    return cv2.bitwise_not(im_floodfill)


def retain_largest_contour(mask2):
    mask = None
    biggest = 0

    contours = measure.find_contours(mask2, 0.0)
    for idx, c in enumerate(contours):
        x = np.zeros(mask2.T.shape, np.uint8)
        cv2.fillPoly(x, [np.int32(c)], 1)
        size = len(np.where(x == 1)[0])
        if size > biggest:
            mask = x
            biggest = size

    mask = ndimage.binary_fill_holes(mask).astype(int)
    mask = 255 * mask.astype(np.uint8)
    return mask.T


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


def process_user_uploaded_segmentation_mask(work_dir, request_file):
    """
    When the user uploads a segmentation mask they've edited, we process it to ensure it is a single polygon without any holes.
    We skip thresholding and morphological operations.
    work_dir: str, location where the mask will be saved
    request_file: werkzeug.datastructures.FileStorage, the uploaded image
    """
    filestr = request_file.read()
    npimg = np.fromstring(filestr, np.uint8)
    im_in_256 = cv2.imdecode(npimg, cv2.IMREAD_UNCHANGED)
    im_in = (im_in_256 != np.array([[[0, 0, 0, 255]]])).any(axis=2).astype(np.uint8)

    cv2.imwrite(os.path.join(work_dir, 'im_in_256.png'), im_in)

    cv2.imwrite(os.path.join(work_dir, 'im_in.png'), im_in * 255)

    fl_img = flood_fill(im_in)

    mask = retain_largest_contour(fl_img)

    cv2.imwrite(os.path.join(work_dir, 'mask.png'), mask)

