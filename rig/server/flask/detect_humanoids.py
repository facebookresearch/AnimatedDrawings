import os
import re
import subprocess, json
from typing import NewType
import cv2
from pathlib import Path
import numpy as np 
import boto3
import base64
import requests
import json 
      

import s3_object

UPLOAD_BUCKET = s3_object.s3_object('dev-demo-sketch-out-interim-files')



DETECTRON2_ENDPOINT = 'http://Model-Zoo-ALB-1822714093.us-east-2.elb.amazonaws.com:5911/predictions/D2_humanoid_detector'

def get_bounding_box_from_torchserve_response(response_json, input_img, orig_dims, small_dims, padding=0):

    # f = open('test_log.txt', 'w')
    # f.write(f'origin dims {orig_dims}\n')
    # f.write(f'small dims {small_dims}\n')

    # if prediction fails, make entire image the bounding box
    if 'boxes' not in response_json.keys() or len(response_json['boxes']) == 0:
        print(f'Bounding box prediction failed. Response: {response_json}')
        return {'x1': 0, 'y1': 0, 'x2': input_img.shape[1], 'y2': input_img.shape[0]}

    # otherwise, find containing box
    x1, y1, x2, y2 = small_dims[1], small_dims[0], 0, 0
    for idx in range(len(response_json['boxes'])):
        _x1, _y1, _x2, _y2 = list(map(int, response_json['boxes'][idx]))
        x1 = min(x1, _x1)
        y1 = min(y1, _y1)
        x2 = max(x2, _x2)
        y2 = max(y2, _y2)

    # f.write(f'small x1 {x1}\n')
    # f.write(f'small x2 {x2}\n')
    # f.write(f'small y1 {y1}\n')
    # f.write(f'small y2 {y2}\n')

    # convert back to image coordinates of the original image
    x1 = int( x1 * orig_dims[1] / small_dims[1])
    x2 = int( x2 * orig_dims[1] / small_dims[1])
    y1 = int( y1 * orig_dims[0] / small_dims[0])
    y2 = int( y2 * orig_dims[0] / small_dims[0])

    # f.write(f'scale_ratio w {orig_dims[1] / small_dims[1]}\n')
    # f.write(f'scale_ratio h {orig_dims[0] / small_dims[0]}\n')

    # f.write(f' x1 {x1}\n')
    # f.write(f' x2 {x2}\n')
    # f.write(f' y1 {y1}\n')
    # f.write(f' y2 {y2}\n')

    # f.close()

    # account for padding
    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)
    x2 = min(input_img.shape[1], x2 + padding)
    y2 = min(input_img.shape[0], y2 + padding)

    return {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}


def image_resize(unique_id, largest_dim = 400, inter = cv2.INTER_AREA):


     # CREATE small_d2_image.png S3 OBJECT
    #resized_path = s3.Object(UPLOAD_BUCKET,unique_id+"small_d2_image.png")
    
    # READ image.png S3 OBJECT as BYTES

    image_obj = UPLOAD_BUCKET.get_object_bytes(unique_id, 'image.png')
    image = cv2.imdecode(np.asarray(bytearray(image_obj)), cv2.IMREAD_COLOR)
  
    (h, w) = image.shape[:2]

    if h >= w:
        max_dim = h
    else:
        max_dim = w

    if max_dim <= largest_dim:

        #PUT image OBJECT to S3
        #resized_path.put(Body=base64.b64encode(image))
        UPLOAD_BUCKET.write_np_to_png_object(unique_id, 'small_d2_image.png', image)
        image = image
        # return image as bytes
        return image, (h, w), (h, w), image

    scale = largest_dim  / max_dim

    reduced_size = (int( h * scale), int(w * scale))

    resized_img = cv2.resize(image, (reduced_size[1], reduced_size[0]), interpolation = inter)
    
    UPLOAD_BUCKET.write_np_to_png_object(unique_id, 'small_d2_image.png', resized_img)
    
    #return resized_img as bytes
    return resized_img, (h, w), reduced_size, image

def detect_humanoids(unique_id):

    resized_img, orig_dims, small_dims, input_img = image_resize(unique_id)

    _, resized_img_buf  = cv2.imencode('.png', resized_img)

    response = requests.post(url=DETECTRON2_ENDPOINT, data=resized_img_buf.tobytes())


    #breakpoint()
    bb_response = response.json()
    bb = get_bounding_box_from_torchserve_response(bb_response, input_img, orig_dims, small_dims, 25)
    
    
    #bb.json
    #bb = base64.b64encode(bb)

    # Serializing json  
    json_object = json.dumps(bb, indent = 4) 
    UPLOAD_BUCKET.write_object(unique_id, "bb.json", json_object)
    
    cropped_img = input_img[bb['y1']:bb['y2'], bb['x1']:bb['x2'], :]
    UPLOAD_BUCKET.write_np_to_png_object(unique_id, 'cropped_image.png', cropped_img)
    
    
    
    
    #data = {"body": new_img}
    
    #response = requests.post(url=DETECTRON2_ENDPOINT, data=testimage)
    #print(response)

    #print(type(resized_img))
    #PUT resized_img OBJECT to s3
    #resized_path.put(Body=base64.b64encode(resized_img))
    #resized_img = base64.b64encode(resized_img)
    #response_json = json.loads(subprocess.check_output(cmd.split(' ')))
    #(resized_img)
    #image_s3 = UPLOAD_BUCKET.get_object_bytes(unique_id, 'small_d2_image.png')
    #print(type(new_img))
    #image = {resized_img':new_img}
    #cmd = f"curl -X POST {DETECTRON2_ENDPOINT} -T {new_img}"
    #response_json = json.loads(subprocess.check_output(cmd.split(' ')))
    #bb = get_bounding_box_from_torchserve_response(response, input_img, orig_dims, small_dims, 25)
    #bb = base64.b64encode(bb)
    #UPLOAD_BUCKET.write_object(unique_id, 'bb.json', bb)
    #print("got bb")


    #cropped_img = input_img[bb['y1']:bb['y2'], bb['x1']:bb['x2'], :]
    #UPLOAD_BUCKET.write_object(unique_id, 'cropped_image.png', cropped_img)
    #print("got cropped")
    #print("success")


#detect_humanoids(unique_id)




#bb = get_bounding_box_from_torchserve_response(response_json, input_img, orig_dims, small_dims, 25)

    #with open(os.path.join(work_dir, 'bb.json'), 'w') as f:
    #    json.dump(bb, f)

    #cropped_img = input_img[bb['y1']:bb['y2'], bb['x1']:bb['x2'], :]

    #cv2.imwrite(os.path.join(work_dir, 'cropped_image.png'), cropped_img)
