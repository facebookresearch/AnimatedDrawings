import os
import json
import cv2, imutils
import numpy as np
from PIL import Image
import io
import storage_service

interim_store = storage_service.get_interim_store()


def crop_from_bb(unique_id):
        # handle image transparancies
        # pull down image from s3 as bytes

        image_data = interim_store.read_bytes(unique_id, "image.png")
        image = Image.open(io.BytesIO(image_data))
        if image.mode == 'P' or 'A' in image.mode:
                input_img = np.array(image.convert('RGBA'))

                # find pixels with val [0, 0, 0, 0]
                pix_eq_0s = np.array(input_img[:, :] == [0, 0, 0, 0])
                transparent_pixels = np.bitwise_and.reduce(pix_eq_0s, axis=2)
                input_img[transparent_pixels, :] = 255  # replace with white
                input_img = input_img[:, :, :-1] # drop alpha layer
                input_img = cv2.cvtColor(input_img, cv2.COLOR_RGB2BGR)

        else:
                input_img = cv2.imdecode(np.fromstring(image_data, np.uint8), 1)
        
        
        #pull down bb.json as bytes
        bb = json.loads(interim_store.read_bytes(unique_id, "bb.json"))

        cropped_img = input_img[bb['y1']:bb['y2'], bb['x1']:bb['x2'], :]

        # resize so largest dim is 400px
        if cropped_img.shape[0] > cropped_img.shape[1]:
                cropped_img = imutils.resize(cropped_img, height=400)
        else:
                cropped_img = imutils.resize(cropped_img, width=400)

        #upload cropped_image.png to s3
        _, enc_cropped_img = cv2.imencode('.png', cropped_img)
        interim_store.write_bytes(unique_id, "cropped_image.png", enc_cropped_img.tobytes())

        ## Create gray blurred version of image for input to pose detector
        bg_cropped_img_ = cv2.cvtColor(cropped_img,cv2.COLOR_BGR2GRAY)
        #  TODO @jesse look into this bg_cropped_img is not used
        bg_cropped_img = cv2.GaussianBlur(bg_cropped_img_,(5,5),0)

        # save data of bg_cropped_img to gray_blur.png
        _, enc_bg_cropped_img = cv2.imencode('.png', cropped_img)
        interim_store.write_bytes(unique_id, "gray_blur.png", enc_bg_cropped_img.tobytes())
