import os
import subprocess, json
import cv2

def get_bounding_box_from_torchserve_response(response_json, input_img, padding=0):

    # if prediction fails, make entire image the bounding box
    if 'boxes' not in response_json.keys() or len(response_json['boxes']) == 0:
        print(f'Bounding box prediction failed. Response: {response_json}')
        return {'x1': 0, 'y1': 0, 'x2': input_img.shape[1], 'y2': input_img.shape[0]}

    # otherwise, find containing box
    x1, y1, x2, y2 = input_img.shape[1], input_img.shape[0], 0, 0
    for idx in range(len(response_json['boxes'])):
        _x1, _y1, _x2, _y2 = list(map(int, response_json['boxes'][idx]))
        x1 = min(x1, _x1)
        y1 = min(y1, _y1)
        x2 = max(x2, _x2)
        y2 = max(y2, _y2)

    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)
    x2 = min(input_img.shape[1], x2 + padding)
    y2 = min(input_img.shape[0], y2 + padding)

    return {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}


def detect_humanoids(work_dir):
    input_img_path = os.path.join(work_dir, 'image.png')

    cmd = f"curl -X POST http://detectron2_server:5911/predictions/D2_humanoid_detector -T {input_img_path}"

    response_json = json.loads(subprocess.check_output(cmd.split(' ')))

    input_img = cv2.imread(input_img_path)
    bb = get_bounding_box_from_torchserve_response(response_json, input_img, 25)

    with open(os.path.join(work_dir, 'bb.json'), 'w') as f:
        json.dump(bb, f)

    cropped_img = input_img[bb['y1']:bb['y2'], bb['x1']:bb['x2'], :]

    cv2.imwrite(os.path.join(work_dir, 'cropped_image.png'), cropped_img)
