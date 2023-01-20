import sys
import requests
import cv2
import json
import numpy as np
from skimage import measure
from scipy import ndimage
from pathlib import Path
import yaml
import logging


def image_to_annotations(img_fn: str, out_dir: str) -> None:
    """
    Given the RGB image located at img_fn, runs detection, segmentation, and pose estimation for drawn character within it.
    Crops the image and saves texture, mask, and character config files necessary for animation. Writes to out_dir.

    Params:
        img_fn: path to RGB image
        out_dir: directory where outputs will be saved
    """

    # read image
    img = cv2.imread(img_fn)

    # ensure it's rgb
    if len(img.shape) != 3:
        msg = f'image must have 3 channels (rgb). Found {len(img.shape)}'
        logging.critical(msg)
        assert False, msg

    # resize if needed
    if np.max(img.shape) > 1000:
        scale = 1000 / np.max(img.shape)
        img = cv2.resize(img, (round(scale * img.shape[1]), round(scale * img.shape[0])))

    # convert to bytes and send to torchserve
    img_b = cv2.imencode('.png', img)[1].tobytes()
    request_data = {'data': img_b}
    resp = requests.post("http://localhost:8080/predictions/drawn_humanoid_detector", files=request_data, verify=False)
    detection_results = json.loads(resp.content)

    # if no drawn humanoids detected, abort
    if len(detection_results) == 0:
        msg = 'Could not detect any drawn humanoids in the image. Aborting'
        logging.critical(msg)
        assert False, msg

    # otherwise, report # detected. Combine bounding boxes if greater than 1
    msg = f'Detected {len(detection_results)} humanoids in image. If more than 1, combining bboxes'
    logging.info(msg)
    bboxes = np.array([d['bbox'] for d in detection_results])
    l, t = [round(f) for f in np.min(bboxes, axis=0)[:2]]
    r, b = [round(f) for f in np.max(bboxes, axis=0)[2:]]

    # crop the image around the character
    cropped = img[t:b, l:r]

    # get segmentation mask
    mask = segment(cropped)

    # send cropped image to pose estimator
    data_file = {'data': cv2.imencode('.png', cropped)[1].tobytes()}
    resp = requests.post("http://localhost:8080/predictions/drawn_humanoid_pose_estimator", files=data_file, verify=False)
    pose_results = json.loads(resp.content)

    # if more than one skeleton detected, abort
    if len(pose_results) == 0:
        msg = 'Could not detect any skeletons within the character bounding box. Expected exactly 1. Aborting.'
        logging.critical(msg)
        assert False, msg

    # if more than one skeleton detected,
    if 1 < len(pose_results):
        msg = f'Detected {len(pose_results)} skeletons with the character bounding box. Expected exactly 1. Aborting.'
        logging.critical(msg)
        assert False, msg

    # get x y coordinates of detection joint keypoints
    kpts = np.array(pose_results[0]['keypoints'])[:, :2]

    # use them to build character skeleton rig
    skeleton = []
    skeleton.append({'loc':[round(x) for x in (kpts[11]+kpts[12])/2], 'name': 'root'          , 'parent': None})
    skeleton.append({'loc':[round(x) for x in (kpts[11]+kpts[12])/2], 'name': 'hip'           , 'parent': 'root'})
    skeleton.append({'loc':[round(x) for x in (kpts[5]+kpts[6])/2  ], 'name': 'torso'         , 'parent': 'hip'})
    skeleton.append({'loc':[round(x) for x in  kpts[0]             ], 'name': 'neck'          , 'parent': 'torso'})
    skeleton.append({'loc':[round(x) for x in  kpts[6]             ], 'name': 'right_shoulder', 'parent': 'torso'})
    skeleton.append({'loc':[round(x) for x in  kpts[8]             ], 'name': 'right_elbow'   , 'parent': 'right_shoulder'})
    skeleton.append({'loc':[round(x) for x in  kpts[10]            ], 'name': 'right_hand'    , 'parent': 'right_elbow'})
    skeleton.append({'loc':[round(x) for x in  kpts[5]             ], 'name': 'left_shoulder' , 'parent': 'torso'})
    skeleton.append({'loc':[round(x) for x in  kpts[7]             ], 'name': 'left_elbow'    , 'parent': 'left_shoulder'})
    skeleton.append({'loc':[round(x) for x in  kpts[9]             ], 'name': 'left_hand'     , 'parent': 'left_elbow'})
    skeleton.append({'loc':[round(x) for x in  kpts[12]            ], 'name': 'right_hip'     , 'parent': 'root'})
    skeleton.append({'loc':[round(x) for x in  kpts[14]            ], 'name': 'right_knee'    , 'parent': 'right_hip'})
    skeleton.append({'loc':[round(x) for x in  kpts[16]            ], 'name': 'right_foot'    , 'parent': 'right_knee'})
    skeleton.append({'loc':[round(x) for x in  kpts[11]            ], 'name': 'left_hip'      , 'parent': 'root'})
    skeleton.append({'loc':[round(x) for x in  kpts[13]            ], 'name': 'left_knee'     , 'parent': 'left_hip'})
    skeleton.append({'loc':[round(x) for x in  kpts[15]            ], 'name': 'left_foot'     , 'parent': 'left_knee'})

    # create the character config dictionary
    char_cfg = {'skeleton': skeleton, 'height': cropped.shape[0], 'width': cropped.shape[1]}

    # create output directory
    outdir = Path(out_dir)
    outdir.mkdir(exist_ok=True)

    # convert texture to RGBA and save
    cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2BGRA)
    cv2.imwrite(str(outdir/'texture.png'), cropped)

    # save mask
    cv2.imwrite(str(outdir/'mask.png'), mask)

    # dump character config to yaml
    with open(str(outdir/'char_cfg.yaml'), 'w') as f:
        yaml.dump(char_cfg, f)

    # create joint viz overlay for inspection purposes
    joint_overlay = cropped.copy()
    for idx in range(np.array(pose_results[0]['keypoints']).shape[0]):
        x, y, _ = pose_results[0]['keypoints'][idx]
        cv2.circle(joint_overlay, (int(x), int(y)), 5, (255, 0, 0), 5)
        cv2.imwrite(str(outdir/'joint_overlay.png'), joint_overlay)


def segment(img: np.ndarray):
    """ threshold """
    img = np.min(img, axis=2)
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 115, 8)
    img = cv2.bitwise_not(img)

    """ morphops """
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel, iterations=2)
    img = cv2.morphologyEx(img, cv2.MORPH_DILATE, kernel, iterations=2)

    """ floodfill """
    mask = np.zeros([img.shape[0]+2, img.shape[1]+2], np.uint8)
    mask[1:-1, 1:-1] = img.copy()

    # im_floodfill is results of floodfill. Starts off all white
    im_floodfill = np.full(img.shape, 255, np.uint8)

    # choose 10 points along each image side. use as seed for floodfill.
    h, w = img.shape[:2]
    for x in range(0, w-1, 10):
        cv2.floodFill(im_floodfill, mask, (x, 0), 0)
        cv2.floodFill(im_floodfill, mask, (x, h-1), 0)
    for y in range(0, h-1, 10):
        cv2.floodFill(im_floodfill, mask, (0, y), 0)
        cv2.floodFill(im_floodfill, mask, (w-1, y), 0)

    # make sure edges aren't character. necessary for contour finding
    im_floodfill[0, :] = 0
    im_floodfill[-1, :] = 0
    im_floodfill[:, 0] = 0
    im_floodfill[:, -1] = 0

    """ retain largest contour """
    mask = None
    biggest = 0

    contours = measure.find_contours(im_floodfill, 0.0)
    for c in contours:
        x = np.zeros(im_floodfill.T.shape, np.uint8)
        cv2.fillPoly(x, [np.int32(c)], 1)
        size = len(np.where(x == 1)[0])
        if size > biggest:
            mask = x
            biggest = size

    if mask is None:
        msg = 'Found no contours within image'
        logging.critical(msg)
        assert False, msg

    mask = ndimage.binary_fill_holes(mask).astype(int)
    mask = 255 * mask.astype(np.uint8)

    return mask.T


if __name__ == '__main__':
    log_dir = Path('./logs')
    log_dir.mkdir(exist_ok=True, parents=True)
    logging.basicConfig(filename=f'{log_dir}/log.txt', level=logging.DEBUG)

    img_fn = sys.argv[1]
    out_dir = sys.argv[2]
    image_to_annotations(img_fn, out_dir)
