import requests
from PIL import Image, ImageOps, ImageSequence
import numpy as np
import sys
import cv2
import json
from skimage import measure
from scipy import ndimage
from pathlib import Path
import yaml
import logging
import uuid
import os.path
from annotations_to_animation import annotations_to_animation


# Function to download and preprocess an image from a given URL
def generate_image(input_url, id, path_to_image):

    url = input_url
    data = requests.get(url).content
    f = open(f'{path_to_image}/{id}.png', 'wb')
    f.write(data)
    f.close()

    img = Image.open(f'{path_to_image}/{id}.png')
    datas = img.getdata()

    new_datas = []

    # Make transparent background white
    for item in datas:
        if item[3] == 0:
            new_datas.append((255, 255, 255))
        else:
            new_datas.append(item)

    img.putdata(new_datas)
    img.save(f'{path_to_image}/{id}.png', 'PNG')
    return img


# Function to merge masks using a template
def merge_masks(im1, im2, outdir):
    mask = Image.open('templates/rectangle_mask.png')
    img = Image.composite(im1, im2, mask)
    img.save(str(outdir/'mask.png'))


def determine_template(url):
    """
    A helper function that determines what template to use when generating
    the merged masks
    Arguments:
        url: the original url of the avatar
    Returns:
        the path to the template
    """
    if "gender=1" in url:
        if "body=0" in url:
            return 'templates/male_templates/male_body_1.png'
        elif "body=3" in url:
            return 'templates/male_templates/male_body_2.png'
        elif "body=5" in url:
            return 'templates/male_templates/male_body_3.png'
        elif "body=1" in url:
            return 'templates/male_templates/male_body_4.png'
        elif "body=2" in url:
            return 'templates/male_templates/male_body_5.png'
        else:
            return 'templates/male_templates/male_body_1.png'
    else:
        if "body=7" in url:
            return 'templates/female_templates/female_body_1.png'
        elif "body=9" in url:
            return 'templates/female_templates/female_body_2.png'
        elif "body=10" in url:
            return 'templates/female_templates/female_body_3.png'
        elif "body=8" in url:
            return 'templates/female_templates/female_body_4.png'
        elif "body=2" in url:
            return 'templates/female_templates/female_body_5.png'
        else:
            return 'templates/female_templates/female_body_1.png'
     

def image_to_annotations(img_fn: str, out_dir: str, path_to_image, url) -> None:
    """
    Given the RGB image located at img_fn, runs detection, segmentation, and pose estimation for drawn character within it.
    Crops the image and saves texture, mask, and character config files necessary for animation. Writes to out_dir.

    Params:
        img_fn: path to RGB image
        out_dir: directory where outputs will be saved
    """

    # create output directory
    outdir = Path(f'{path_to_image}/{out_dir}')
    outdir.mkdir(exist_ok=True)

    # read image
    img = cv2.imread(img_fn)

    # copy the original image into the output_dir
    cv2.imwrite(str(outdir/'image.png'), img)

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
    if resp is None or resp.status_code >= 300:
        raise Exception(f"Failed to get bounding box, please check if the 'docker_torchserve' is running and healthy, resp: {resp}")

    detection_results = json.loads(resp.content)

    # error check detection_results
    if type(detection_results) == dict and 'code' in detection_results.keys() and detection_results['code'] == 404:
        assert False, f'Error performing detection. Check that drawn_humanoid_detector.mar was properly downloaded. Response: {detection_results}'

    # order results by score, descending
    detection_results.sort(key=lambda x: x['score'], reverse=True)

    # if no drawn humanoids detected, abort
    if len(detection_results) == 0:
        msg = 'Could not detect any drawn humanoids in the image. Aborting'
        logging.critical(msg)
        assert False, msg

    # otherwise, report # detected and score of highest.
    msg = f'Detected {len(detection_results)} humanoids in image. Using detection with highest score {detection_results[0]["score"]}.'
    logging.info(msg)

    # calculate the coordinates of the character bounding box
    l, t, r, b = [145, 31, 474, 950]

    # dump the bounding box results to file
    with open(str(outdir/'bounding_box.yaml'), 'w') as f:
        yaml.dump({
            'left': l,
            'top': t,
            'right': r,
            'bottom': b
        }, f)

    # crop the image
    cropped = img[t:b, l:r]

    # get segmentation mask
    mask = segment(cropped)

    # send cropped image to pose estimator
    data_file = {'data': cv2.imencode('.png', cropped)[1].tobytes()}
    resp = requests.post("http://localhost:8080/predictions/drawn_humanoid_pose_estimator", files=data_file, verify=False)
    if resp is None or resp.status_code >= 300:
        raise Exception(f"Failed to get skeletons, please check if the 'docker_torchserve' is running and healthy, resp: {resp}")

    pose_results = json.loads(resp.content)

    # error check pose_results
    if type(pose_results) == dict and 'code' in pose_results.keys() and pose_results['code'] == 404:
        assert False, f'Error performing pose estimation. Check that drawn_humanoid_pose_estimator.mar was properly downloaded. Response: {pose_results}'

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
    skeleton.append({'loc' : [round(x) for x in (kpts[11]+kpts[12])/2], 'name': 'root'          , 'parent': None})
    skeleton.append({'loc' : [round(x) for x in (kpts[11]+kpts[12])/2], 'name': 'hip'           , 'parent': 'root'})
    skeleton.append({'loc' : [round(x) for x in (kpts[5]+kpts[6])/2  ], 'name': 'torso'         , 'parent': 'hip'})
    skeleton.append({'loc' : [round(x) for x in  kpts[0]             ], 'name': 'neck'          , 'parent': 'torso'})
    skeleton.append({'loc' : [round(x) for x in  kpts[6]             ], 'name': 'right_shoulder', 'parent': 'torso'})
    skeleton.append({'loc' : [round(x) for x in  kpts[8]             ], 'name': 'right_elbow'   , 'parent': 'right_shoulder'})
    skeleton.append({'loc' : [round(x) for x in  kpts[10]            ], 'name': 'right_hand'    , 'parent': 'right_elbow'})
    skeleton.append({'loc' : [round(x) for x in  kpts[5]             ], 'name': 'left_shoulder' , 'parent': 'torso'})
    skeleton.append({'loc' : [round(x) for x in  kpts[7]             ], 'name': 'left_elbow'    , 'parent': 'left_shoulder'})
    skeleton.append({'loc' : [round(x) for x in  kpts[9]             ], 'name': 'left_hand'     , 'parent': 'left_elbow'})
    skeleton.append({'loc' : [round(x) for x in  kpts[12]            ], 'name': 'right_hip'     , 'parent': 'root'})
    skeleton.append({'loc' : [round(x) for x in  kpts[14]            ], 'name': 'right_knee'    , 'parent': 'right_hip'})
    skeleton.append({'loc' : [round(x) for x in  kpts[16]            ], 'name': 'right_foot'    , 'parent': 'right_knee'})
    skeleton.append({'loc' : [round(x) for x in  kpts[11]            ], 'name': 'left_hip'      , 'parent': 'root'})
    skeleton.append({'loc' : [round(x) for x in  kpts[13]            ], 'name': 'left_knee'     , 'parent': 'left_hip'})
    skeleton.append({'loc' : [round(x) for x in  kpts[15]            ], 'name': 'left_foot'     , 'parent': 'left_knee'})

    # create the character config dictionary
    char_cfg = {'skeleton': skeleton, 'height': cropped.shape[0], 'width': cropped.shape[1]}

    # convert texture to RGBA and save
    cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2BGRA)
    cv2.imwrite(str(outdir/'texture.png'), cropped)

    # save mask
    cv2.imwrite(str(outdir/'mask_original.png'), mask)

    template = determine_template(url)
    merge_masks(Image.open(str(outdir/'mask_original.png')), Image.open(template), outdir)

    # dump character config to yaml
    with open(str(outdir/'char_cfg.yaml'), 'w') as f:
        yaml.dump(char_cfg, f)

    # create joint viz overlay for inspection purposes
    joint_overlay = cropped.copy()
    for joint in skeleton:
        x, y = joint['loc']
        name = joint['name']
        cv2.circle(joint_overlay, (int(x), int(y)), 5, (0, 0, 0), 5)
        cv2.putText(joint_overlay, name, (int(x), int(y+15)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, 2)
    cv2.imwrite(str(outdir/'joint_overlay.png'), joint_overlay)

    return outdir


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
    mask2 = cv2.bitwise_not(im_floodfill)
    mask = None
    biggest = 0

    contours = measure.find_contours(mask2, 0.0)
    for c in contours:
        x = np.zeros(mask2.T.shape, np.uint8)
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

# Main function for execution
def my_exec(url, out_dir, path_to_image):
    log_dir = Path('./logs')
    log_dir.mkdir(exist_ok=True, parents=True)
    logging.basicConfig(filename=f'{log_dir}/log.txt', level=logging.DEBUG)


    # Generate image from URL
    generate_image(url, out_dir, path_to_image)
    img_fn = f'{path_to_image}/{out_dir}.png'

    # Process image and generate annotations
    outdir = image_to_annotations(img_fn, out_dir, path_to_image, url)


    # make directory to store all animations within outdir named "animations"
    animations_outdir = Path(f'{outdir}/animations')
    animations_outdir.mkdir(exist_ok=True)


    # Process motion configurations and generate animations
    for motion_cfg_fn in os.listdir('./config/custom_avatar_animations'):
        if '.yaml' in motion_cfg_fn:
            motion_name = motion_cfg_fn[:len(motion_cfg_fn)-5]
            print(f"Processing {motion_name}...")
            annotations_to_animation(outdir, f'./config/custom_avatar_animations/{motion_cfg_fn}', 'config/retarget/retarget_custom_avatar_animations.yaml')
            os.rename(f'{outdir}/video.gif', f'{animations_outdir}/{motion_name}.gif')
        
    # generate animation to kick right by reversing initial kicking animation
    kicking_left_gif = Image.open(f'{animations_outdir}/kicking_left.gif')
    reverse_frames = [ImageOps.mirror(frame.copy()) for frame in ImageSequence.Iterator(kicking_left_gif)]
    reverse_frames[0].save(f'{animations_outdir}/kicking_right.gif', format='GIF', save_all=True, disposal=2, append_images=reverse_frames[1:])

# Main entry point of the script
if __name__ == '__main__':
    # Get URL from command line argument
    url = sys.argv[1]
    if len(sys.argv) > 2:
        out_dir = sys.argv[2]
    else:
        out_dir = uuid.uuid1()
    # Execute the processing
    my_exec(url, out_dir, "./custom_avatars")

