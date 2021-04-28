from PIL import Image, ImageFilter, ImageDraw
import os
import numpy as np
from skimage import measure
from sklearn.cluster import KMeans


def convert_grayscale_and_blur(input_fn, output_fn, blur_radius):
    """
    Create a grayscale blurred version of an image
    :param input_fn: input image filename
    :param output_fn: output filename to save processed image
    :param blur_radius: Gaussian blur radius parameter
    :return:
    """
    if not os.path.exists(input_fn) or not input_fn.split('.')[-1] in ['png']:
        assert False
    Image.open(input_fn).convert('L').filter(ImageFilter.GaussianBlur(radius=blur_radius)).save(output_fn)


def convert_image(img, pixel_val_in, pixel_val_out):
    """
    Replaces all pixels of a specific value with another value within img. RGB and RGBA mode only.
    :param img: the image (PIL.Image)
    :param pixel_val_in: the pixel value to replace
    :param pixel_val_out: the value to replace pixel_val_in with
    :return: PIL.Image
    """
    assert img.mode in ['RGB', 'RGBA']
    data = np.array(img)  # "data" is a height x width x 4 numpy array

    if len(pixel_val_in) == 3:
        r, g, b = pixel_val_in
        red, green, blue = data.T  # Temporarily unpack the bands for readability
        selected_pixels = (red == r) & (blue == b) & (green == g)
        data[...][selected_pixels.T] = pixel_val_out  # Transpose back needed
    elif len(pixel_val_in) == 4:
        r, g, b, a = pixel_val_in
        red, green, blue, alpha = data.T  # Temporarily unpack the bands for readability
        selected_pixels = (red == r) & (blue == b) & (green == g) & (alpha == a)
        data[...][selected_pixels.T] = pixel_val_out  # Transpose back needed
    else:
        assert False, "pixel_val_in not 3 or 4"
    return Image.fromarray(data)


def convert_image2(img, img2, pixel_val_in, pixel_val_out):
    """
    Finds all pixels in img that match pixel_val_in. Then, updates the corresponding pixels
    in img2 with pixel_val_out. Returns updated img2.
    :param img:
    :param img2:
    :param pixel_val_in:
    :param pixel_val_out:
    :return: PIL.Image
    """
    assert img.mode in ['RGB', 'RGBA']
    assert img2.mode in ['RGB', 'RGBA']
    assert img.size == img2.size

    data = np.array(img)  # "data" is a height x width x 4 numpy array
    data2 = np.array(img2)  # "data" is a height x width x 4 numpy array

    if len(pixel_val_in) == 3:
        r, g, b = pixel_val_in
        red, green, blue = data.T  # Temporarily unpack the bands for readability
        selected_pixels = (red == r) & (blue == b) & (green == g)
        data2[...][selected_pixels.T] = pixel_val_out  # Transpose back needed
    elif len(pixel_val_in) == 4:
        r, g, b, a = pixel_val_in
        red, green, blue, alpha = data.T  # Temporarily unpack the bands for readability
        selected_pixels = (red == r) & (blue == b) & (green == g) & (alpha == a)
        data2[...][selected_pixels.T] = pixel_val_out  # Transpose back needed
    else:
        assert False, "pixel_val_in not 3 or 4"
    return Image.fromarray(data2)


def mask_from_floodfill(img, t_val, seeds=[]):
    """
    Given an image and a threshold value, performs a flood fill from the four corners,
    finds the largest polygon that hasn't been floodfills, and returns a mask of it.
    :param img: The image to floodfill
    :param t_val: The threshold value used in the floodfill step
    :return: (mask <PIL.Image>, contour <np.array[:,2]>
    """
    img = img.copy()
    seeds += [ (0, 0), (0, img.size[1] - 1), (img.size[0] - 1, 0), (img.size[0] - 1, img.size[1] - 1)]
    for seed in seeds:
        ImageDraw.floodfill(img, seed, (0, 0, 0), thresh=t_val)

    # find the largest shape in mask using contour. assume this is the character and remove everything else
    _mask = Image.new(mode='RGB', size=img.size, color=(255, 255, 255))
    mask = convert_image2(img, _mask, (0, 0, 0), (0, 0, 0))
    mask_np = np.array(mask.convert('1'))
    mask_np[ 0,  :] = 0  # make sure no border pixels are black, this can make contour finding fail
    mask_np[-1,  :] = 0
    mask_np[ :,  0] = 0
    mask_np[ :, -1] = 0
    contours = measure.find_contours(mask_np, 0.5)
    contour, max_c_len = None, 0
    for c in contours:
        if len(c) > max_c_len:
            contour, max_c_len = c, len(c)
    assert contour is not None

    mask = Image.new(mode='RGB', size=img.size, color=(0, 0, 0))
    draw = ImageDraw.Draw(mask)
    contour[:, :] = contour[:, [1, 0]]  # swap x and y
    draw.polygon(list(map(int, contour.flatten())), fill=(255, 255, 255))

    return mask, contour


def get_bbox_from_mask(mask, mode="xxyy"):
    """
    Given an RGB image, returns a bounding box of all non-black pixlels
    :param mask:
    :return: bbox
    """
    assert mask.mode == 'RGB'
    img = np.array(mask)
    a = np.where(img != [0, 0, 0])
    if mode=="xxyy":  # left, right, top, bottom
        bbox = np.min(a[1]), np.max(a[1]), np.min(a[0]), np.max(a[0])
        return bbox
    elif mode == 'cxcywh':  #center, width, height
        l, r, t, b = np.min(a[1]), np.max(a[1]), np.min(a[0]), np.max(a[0])
        cx = int((l + r) / 2)
        cy = int((t + b) / 2)
        w = r - l
        h = b - t
        return int(cx), int(cy), int(w), int(h)
    else:
        assert False, 'mode not recognized: {}'.format(mode)


def get_optimal_k_via_elbow(img_np, low=1, high=4):
    """
    given a numpy array image, will perform kmeans pixel clustering with clusters counts between low and high.
    Checks the difference in inertia between different cluster counts, and returns the elbow value.
    See here: https://en.wikipedia.org/wiki/Elbow_method_(clustering)
    :param img_np: numpy array of the image
    :return: integer indicating optimal number of clusters
    """
    md = []
    for k in range(low, high):
        kmeans = KMeans(n_clusters=k)
        kmeans.fit(img_np)
        o = kmeans.inertia_
        md.append(o)
    mdd = []
    for idx, val in enumerate(md):
        if idx == 0 or idx == len(md) - 1:
            mdd.append(0)
        else:
            mdd.append((md[idx - 1] - md[idx]) - (md[idx] - md[idx - 1]))

    elbow_optimal_k = mdd.index(max(mdd)) + 1
    return elbow_optimal_k


def get_shrunk_and_centered_image(_img, width=400, height=400, color=(255, 255, 255)):
    """Given an image and the dimensions of a new canvas, will shrink the image to fit and center it
    in the new canvas"""
    img = _img.copy()
    if type(_img) == np.ndarray:
        img = Image.fromarray(img)

    img.thumbnail((width, height))

    ret_img = Image.new(mode=img.mode, size=(width, height), color=color)

    top_x = int((width - img.size[0])/2)
    top_y = int((height - img.size[1])/2)
    ret_img.paste(img, (top_x, top_y))

    if type(_img) == np.ndarray:
        ret_img = np.array(ret_img)

    return ret_img


def cv2_imfloodfill(_im_in):
    import cv2

    # Read image
    # im_in = cv2.imread("nickel.jpg", cv2.IMREAD_GRAYSCALE);

    # Threshold.
    # Set values equal to or above 220 to 0.
    # Set values below 220 to 255.
    _im_in = cv2.bitwise_not(_im_in.copy())

    # Generate intermediate image; use morphological closing to keep parts of the brain together
    im_in = cv2.morphologyEx(_im_in, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))

    th, im_th = cv2.threshold(im_in, 220, 255, cv2.THRESH_BINARY_INV);

    # Copy the thresholded image.
    im_floodfill = im_th.copy()

    # Mask used to flood filling.
    # Notice the size needs to be 2 pixels than the image.
    h, w = im_th.shape[:2]
    mask = np.zeros((h+2, w+2), np.uint8)

    # Floodfill from point (0, 0)
    cv2.floodFill(im_floodfill, mask, (0,0), 255);

    # Invert floodfilled image
    im_floodfill_inv = cv2.bitwise_not(im_floodfill)

    # Combine the two images to get the foreground.
    im_floodfilled = im_th | im_floodfill_inv

    out = np.zeros(im_floodfilled.shape, np.uint8)

    # Find largest contour in intermediate image
    try:
        cnts, _ = cv2.findContours(im_floodfilled, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cnt = max(cnts, key=cv2.contourArea)
        cv2.drawContours(out, [cnt], -1, 255, cv2.FILLED)
    except:
        print('no contours found in img. skipping')

    # Output
    im_out = cv2.bitwise_and(im_floodfilled, out)
    return im_out

import math
def get_image_composite(image_locs, _cols=5):
    """
    given a list of image paths or a list of PIL image object, returns a composite of them. images must be same size
    :param image_locs: list(str), path and name of images
    :param _cols:  number of columns in composite
    :return: PIL Image
    """
    cols = _cols
    rows = math.ceil(len(image_locs) / cols)

    if type(image_locs[0]) == str:
        img_w, img_h = Image.open(image_locs[0]).size  # all images number be same size. Get this to check
    elif type(image_locs[0]) == Image.Image:
        img_w, img_h = image_locs[0].size
    else:
        assert False

    composite = Image.new(mode='RGB', size=(cols*img_w, rows*img_h), color=(0, 0, 0))
    for idx, loc in enumerate(image_locs):
        try:
            if type(image_locs[0]) == str:
                img = Image.open(loc)
            else:
                img = loc
        except:
            img = Image.new(mode='RGB', size=(img_w, img_h), color=(0, 0, 0))
            print('Could not open file or is wrong size: {}. Skipping it.'.format(loc))

        assert img_w, img_h == img.size
        insert_x = (idx % cols) * img_w
        insert_y = math.floor(idx / cols) * img_h
        composite.paste(img, (insert_x, insert_y))
    return composite

if __name__ == '__main__':
    x = 2
