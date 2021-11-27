import os, sys
import subprocess, json
import requests
import s3_object


UPLOAD_BUCKET = s3_object.s3_object('dev-demo-sketch-out-interim-files')


ALPHAPOSE_ENDPOINT = 'http://ecs-sketch-animation-alb-275652448.us-east-2.elb.amazonaws.com:5912/predictions/alphapose'

def detect_pose(unique_id):
    #uuid = work_dir.split('/')[-1]
    #img_pth = os.path.abspath(os.path.join(work_dir, 'gray_blur.png'))
    #pull form s3 as bytes
    img_bytes = UPLOAD_BUCKET.get_object_bytes(unique_id, 'gray_blur.png')

    #cmd = f"curl -X POST -F uuid={uuid} -F image=@{img_pth} http://ecs-sketch-animation-alb-275652448.us-east-2.elb.amazonaws.com:5912/predictions/alphapose"
    # response_json = requests.post(url=ALPHAPOSE_ENDPOINT, data=img_pth) # this is for the new alphapose.mar file. To use the one currently in production, requests should be in the form below
    response_json = requests.post(url=ALPHAPOSE_ENDPOINT, data={'uuid': unique_id, 'image':img_bytes})

    #save alphapose_results.json' under uuid directory in interim bucket
    # with open(os.path.join(work_dir, 'alphapose_results.json'), 'w') as f:
    #     json.dump(response_json, f)
    try:
        json_object = json.dumps(response_json.json(), indent = 4) 
    except:
        assert False  # TODO @Chris - I'm intermittantly getting a 503 error response when querying ALPHAPOSE_ENPOINT
    UPLOAD_BUCKET.write_object(unique_id, "alphapose_results.json", json_object)

    #UPLOAD_BUCKET.write_object(unique_id, 'alphapose_results.json', response_json.json())

    keypoint_names=[
        "nose", "left_eye", "right_eye", "left_ear", "right_ear",
        "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
        "left_wrist", "right_wrist", "left_hip", "right_hip",
        "left_knee", "right_knee", "left_ankle", "right_ankle"]
    k_iter = iter(response_json.json()['keypoints'])

    joint_locations = {}
    for name, (x, y, _) in zip(keypoint_names, zip(k_iter, k_iter, k_iter)):
        joint_locations[name] = {'x': int(x), 'y': int(y)}


    #save joint_locations.json to s3
    joint_locations_s = json.dumps(joint_locations, indent = 4) 
    UPLOAD_BUCKET.write_object(unique_id, "joint_locations.json", joint_locations_s)

    # output_loc = os.path.join(work_dir, 'joint_locations.json')
    # with open(output_loc, 'w') as f:
    #     json.dump(joint_locations, f)
