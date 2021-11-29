import json
import numpy as np
import cv2
import requests

url1='http://localhost:5000/upload_image'
with open('image2.png', 'rb') as f:
    testimage = f.read()
files = {'file': testimage}
response = requests.post(url=url1, files=files)

uuid = response.text

url2='http://localhost:5000/get_bounding_box_coordinates'
response = requests.post(url=url2, data={'uuid':uuid})
bbs = response.text

url3='http://localhost:5000/set_bounding_box_coordinates'
response = requests.post(url=url3, data={'uuid':uuid, 'bounding_box_coordinates':bbs})

url4='http://localhost:5000/get_mask'
response = requests.post(url=url4, data={'uuid':uuid})
mask = cv2.imdecode(np.frombuffer(response.content, np.uint8), 1)

url5='http://localhost:5000/set_mask'
files = {'file': mask.tobytes()}
data = {'uuid':uuid}
response = requests.post(url=url5, data=data, files=files)

url6='http://localhost:5000/get_joint_locations_json'
data = {'uuid':uuid}
response = requests.post(url=url6, data=data)
joint_locs = json.loads(response.text)

url7='http://localhost:5000/set_joint_locations_json'
data = {'uuid':uuid, 'joint_location_json':json.dumps(joint_locs)}
response = requests.post(url=url7, data=data)

url8='http://localhost:5000/get_image'
data = {'uuid':uuid}
response = requests.post(url=url8, data=data)

url9='http://localhost:5000/get_cropped_image'
data = {'uuid':uuid}
response = requests.post(url=url9, data=data)

url10='http://localhost:5000/set_consent_answer'
data = {'uuid':uuid, 'consent_response':'0'}
response = requests.post(url=url10, data=data)

url11='http://localhost:5000/get_animation'
data = {'uuid':uuid, 'animation':'boxing'}
response = requests.post(url=url11, data=data)
