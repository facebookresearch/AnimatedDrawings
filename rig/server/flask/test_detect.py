import os
import subprocess, json
import cv2
from pathlib import Path
import numpy as np 
import boto3
import base64
import requests


s3 = boto3.resource('s3')


UPLOAD_BUCKET='dev-demo-sketch-out-interim-files'
unique_id = 'a5a09f5b6b844e009061c77216f2406d-API-TEST'
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


def image_resize(input_img_path, largest_dim = 400, inter = cv2.INTER_AREA):


     # CREATE small_d2_image.png S3 OBJECT
    resized_path = s3.Object(UPLOAD_BUCKET,unique_id+"small_d2_image.png")
    
    # READ image.png S3 OBJECT as BYTES
    image_obj = s3.Object(UPLOAD_BUCKET, unique_id+"/image.png").get().get('Body').read()

    image = cv2.imdecode(np.asarray(bytearray(image_obj)), cv2.IMREAD_COLOR)
    (h, w) = image.shape[:2]
    if h >= w:
        max_dim = h
    else:
        max_dim = w

    if max_dim <= largest_dim:

        #PUT image OBJECT to S3
        resized_path.put(Body=base64.b64encode(image))
        return resized_path, (h, w), (h, w)

    scale = largest_dim  / max_dim

    reduced_size = (int( h * scale), int(w * scale))

    resized_img = cv2.resize(image, (reduced_size[1], reduced_size[0]), interpolation = inter)
    

    #PUT resized_img OBJECT to s3
    resized_path.put(Body=base64.b64encode(resized_img))
    
    return resized_path, (h, w), reduced_size

def detect_humanoids(unique_id):
    object_url = "https://%s.s3.us-east-2.amazonaws.com/%s-API-TEST/image.png" % (UPLOAD_BUCKET,unique_id)

    get_obj = s3.Object(UPLOAD_BUCKET, unique_id+"/image.png")
    image_obj = get_obj.get()['Body']

    resized_img_path, orig_dims, small_dims = image_resize(object_url)
    get_obj = s3.Object(UPLOAD_BUCKET, unique_id+"/small_d2_image.png")
    image_obj = get_obj.get()['Body'].read()
    requests.post(url=DETECTRON2_ENDPOINT, data=image_obj)