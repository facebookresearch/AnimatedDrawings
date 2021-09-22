import os
import json
import cv2, imutils
import numpy as np
from PIL import Image

def crop_from_bb(work_dir):
        # handle image transparancies
        input_img = Image.open(os.path.join(work_dir, 'image.png'))
        if input_img.mode == 'P' or 'A' in input_img.mode:
                input_img = np.array(input_img.convert('RGBA'))

                # find pixels with val [0, 0, 0, 0]
                pix_eq_0s = np.array(input_img[:, :] == [0, 0, 0, 0])
                transparent_pixels = np.bitwise_and.reduce(pix_eq_0s, axis=2)
                input_img[transparent_pixels, :] = 255  # replace with white
                input_img = input_img[:, :, :-1] # drop alpha layer
                input_img = cv2.cvtColor(input_img, cv2.COLOR_RGB2BGR)

        else:
                input_img = cv2.imread(os.path.join(work_dir, 'image.png'))

        with open(os.path.join(work_dir, 'bb.json'), 'r') as f:
            bb = json.load(f)

        cropped_img = input_img[bb['y1']:bb['y2'], bb['x1']:bb['x2'], :]

        # resize so largest dim is 400px
        if cropped_img.shape[0] > cropped_img.shape[1]:
                cropped_img = imutils.resize(cropped_img, height=400)
        else:
                cropped_img = imutils.resize(cropped_img, width=400)

        cv2.imwrite(os.path.join(work_dir, 'cropped_image.png'), cropped_img)

        ## Create gray blurred version of image for input to pose detector
        bg_cropped_img_ = cv2.cvtColor(cropped_img,cv2.COLOR_BGR2GRAY)
        bg_cropped_img = cv2.GaussianBlur(bg_cropped_img_,(5,5),0)

        bg_output_path = os.path.join(work_dir, 'gray_blur.png')

        cv2.imwrite(bg_output_path, bg_cropped_img)

        ## Create sketch-DET.json for input to pose detector
        h, w = cropped_img.shape[:2]
        cx, cy = int(w/2), int(h/2)
        det = [{
                'category_id':1,
                'score':0.9,
                'bbox': (cx, cy, w, h),
                'image_id': f'{os.path.abspath(bg_output_path)}',
        }]
        with open(os.path.join(work_dir, 'sketch-DET.json'), 'w') as f:
                json.dump(det, f)

