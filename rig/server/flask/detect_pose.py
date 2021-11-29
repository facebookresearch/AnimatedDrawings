import os, sys
import subprocess, json
import requests
import storage_service



interim_store = storage_service.get_interim_store()

ALPHAPOSE_ENDPOINT = os.environ.get("ALPHAPOSE_ENDPOINT")

def detect_pose(unique_id):
    #uuid = work_dir.split('/')[-1]
    #img_pth = os.path.abspath(os.path.join(work_dir, 'gray_blur.png'))
    #pull form s3 as bytes
    img_bytes = interim_store.read_bytes(unique_id, 'gray_blur.png')

    response_json = requests.post(url=ALPHAPOSE_ENDPOINT, data={'uuid': unique_id, 'image':img_bytes})

    #save alphapose_results.json' under uuid directory in interim bucket
    # with open(os.path.join(work_dir, 'alphapose_results.json'), 'w') as f:
    #     json.dump(response_json, f)
    try:
        json_object = json.dumps(response_json.json(), indent = 4) 
    except:
        assert False  # TODO @Chris - I'm intermittantly getting a 503 error response when querying ALPHAPOSE_ENPOINT
    interim_store.write_bytes(unique_id, "alphapose_results.json",  bytearray(json_object, "ascii") )


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
    interim_store.write_bytes(unique_id, "joint_locations.json", bytearray(joint_locations_s, "ascii") )

    # output_loc = os.path.join(work_dir, 'joint_locations.json')
    # with open(output_loc, 'w') as f:
    #     json.dump(joint_locations, f)
