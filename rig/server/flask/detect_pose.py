import os, sys
import subprocess, json
import requests
import storage_service
import numpy as np
import cv2


import logging
gunicorn_logger = logging.getLogger('gunicorn.error')

if gunicorn_logger:
    root_logger = logging.getLogger()
    root_logger.handlers = gunicorn_logger.handlers
    root_logger.setLevel(gunicorn_logger.level)

interim_store = storage_service.get_interim_store()

ALPHAPOSE_ENDPOINT = os.environ.get("ALPHAPOSE_ENDPOINT")

MMPOSE_ENDPOINT = os.environ.get("MMPOSE_ENDPOINT")

def detect_pose(unique_id, is_sparkar_request=False):

    if is_sparkar_request:
        detect_pose_mmpose(unique_id)
    else:
        detect_pose_alphapose(unique_id)


def detect_pose_mmpose(unique_id):
    root_logger.log(logging.INFO, f'detecting joints with mmpose')

    img_bytes = interim_store.read_bytes(unique_id, 'cropped_image.png')

    response_json = requests.post(url=MMPOSE_ENDPOINT, data=img_bytes)

    json_object = json.dumps(response_json.json()[0], indent = 4)

    interim_store.write_bytes(unique_id, "mmpose_results.json",  bytearray(json_object, "ascii") )

    img_np = cv2.imdecode(np.asarray(bytearray(img_bytes)), 1)
    h, w = img_np.shape[0:2]

    keypoint_names=[
        "nose", "left_eye", "right_eye", "left_ear", "right_ear",
        "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
        "left_wrist", "right_wrist", "left_hip", "right_hip",
        "left_knee", "right_knee", "left_ankle", "right_ankle"]

    keypoints = response_json.json()[0]['keypoints']

    joint_locations = {}
    for name, (_x, _y, _) in zip(keypoint_names, keypoints):
        x = int(max(0, min(w, _x)))  # clamp x to int between 0 and img w
        y = int(max(0, min(h, _y)))  # clamp y to int between 0 and img h

        joint_locations[name] = {'x': x, 'y': y}

    joint_locations_s = json.dumps(joint_locations, indent = 4)
    interim_store.write_bytes(unique_id, "joint_locations.json", bytearray(joint_locations_s, "ascii") )


def detect_pose_alphapose(unique_id):
    root_logger.log(logging.INFO, f'detecting joints with AlphaPose')

    img_bytes = interim_store.read_bytes(unique_id, 'cropped_image.png')

    response_json = requests.post(url=ALPHAPOSE_ENDPOINT, data={'uuid': unique_id, 'image':img_bytes})

    json_object = json.dumps(response_json.json(), indent = 4)

    interim_store.write_bytes(unique_id, "alphapose_results.json",  bytearray(json_object, "ascii") )

    img_np = cv2.imdecode(np.asarray(bytearray(img_bytes)), 1)
    h, w = img_np.shape[0:2]

    keypoint_names=[
        "nose", "left_eye", "right_eye", "left_ear", "right_ear",
        "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
        "left_wrist", "right_wrist", "left_hip", "right_hip",
        "left_knee", "right_knee", "left_ankle", "right_ankle"]
    k_iter = iter(response_json.json()['keypoints'])

    joint_locations = {}
    for name, (_x, _y, _) in zip(keypoint_names, zip(k_iter, k_iter, k_iter)):
        x = int(max(0, min(w, _x)))  # clamp x to int between 0 and img w
        y = int(max(0, min(h, _y)))  # clamp y to int between 0 and img h

        joint_locations[name] = {'x': x, 'y': y}

    joint_locations_s = json.dumps(joint_locations, indent = 4)
    interim_store.write_bytes(unique_id, "joint_locations.json", bytearray(joint_locations_s, "ascii") )
