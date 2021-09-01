import json
import sys
import os

json_loc = os.path.join(sys.argv[1], 'alphapose_results.json')
output_loc = os.path.join(sys.argv[1], 'joint_locations.json')

with open(json_loc, 'r') as f:
    data = json.load(f)

keypoint_names=[
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle"]
k_iter = iter(data[0]['keypoints'])

joint_locations = {}
for name, (x, y, c) in zip(keypoint_names, zip(k_iter, k_iter, k_iter)):
    joint_locations[name] = {'x': int(x), 'y': int(y)}

with open(output_loc, 'w') as f:
    json.dump(joint_locations, f)
