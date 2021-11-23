import os, sys
import subprocess, json
import requests
ANIMATION_ENDPOINT = 'http://ecs-sketch-animation-alb-275652448.us-east-2.elb.amazonaws.com:5912/predictions/alphapose'

def detect_pose(work_dir):
    uuid = work_dir.split('/')[-1]
    img_pth = os.path.abspath(os.path.join(work_dir, 'gray_blur.png'))
    #pull form s3 as bytes
    #cmd = f"curl -X POST -F uuid={uuid} -F image=@{img_pth} http://ecs-sketch-animation-alb-275652448.us-east-2.elb.amazonaws.com:5912/predictions/alphapose"
    response_json = requests.post(url=ANIMATION_ENDPOINT, data=img_pth)

    #save alphapose_results.json' under uuid directory in interim bucket
    with open(os.path.join(work_dir, 'alphapose_results.json'), 'w') as f:
        json.dump(response_json, f)

    keypoint_names=[
        "nose", "left_eye", "right_eye", "left_ear", "right_ear",
        "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
        "left_wrist", "right_wrist", "left_hip", "right_hip",
        "left_knee", "right_knee", "left_ankle", "right_ankle"]
    k_iter = iter(response_json['keypoints'])

    joint_locations = {}
    for name, (x, y, _) in zip(keypoint_names, zip(k_iter, k_iter, k_iter)):
        joint_locations[name] = {'x': int(x), 'y': int(y)}


    #save joint_locations.json to s3
    output_loc = os.path.join(work_dir, 'joint_locations.json')
    with open(output_loc, 'w') as f:
        json.dump(joint_locations, f)
