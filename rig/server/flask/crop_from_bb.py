import os
import json
import cv2, imutils

def crop_from_bb(work_dir):
        gray_blur_img_out_loc = os.path.join(work_dir, 'gray_blur.png')
        sketch_DET_loc = os.path.join(work_dir, 'sketch-DET.json')

        # Create cropped image
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

