import cv2
import json
import requests
from pathlib import Path

imgdir_p = Path('a_input_images_small')

ALPHAPOSE_ENDPOINT = "http://localhost:5912/predictions/alphapose"

for item in imgdir_p.glob('*.png'):

    with open(str(item), 'rb') as reader:
        img_bytes = reader.read()

    response_json = requests.post(url=ALPHAPOSE_ENDPOINT, data={'image':img_bytes})
    json_object = json.loads(response_json._content)

    k_iter = iter(json_object['keypoints'])
    img = cv2.imread(str(item))

    for x, y, _ in zip(k_iter, k_iter, k_iter):
        x, y = int(x), int(y)
        img[y-1:y+1,x-1:x+1] = [0, 0, 255]

    cv2.imwrite(f'out/{item.stem}_viz.png', img)



