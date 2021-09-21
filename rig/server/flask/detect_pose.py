import os, sys
import subprocess, json

def detect_pose(work_dir):
    cmd = f"curl -d det_file_loc={work_dir}/sketch-DET.json http://localhost:5911/predictions/alphapose"

    response_json = json.loads(subprocess.check_output(cmd.split(' ')))

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

    output_loc = os.path.join(work_dir, 'joint_locations.json')
    with open(output_loc, 'w') as f:
        json.dump(joint_locations, f)
