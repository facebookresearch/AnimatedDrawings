import logging
import sys
import requests
import cv2
import os
import numpy as np
from pathlib import Path
from PIL import Image

def generate_talking_animations(url, out_dir):

    # creates the directory to store the animation
    outdir = Path(out_dir)
    outdir.mkdir(exist_ok=True)

    # creates the initial image using the url
    data = requests.get(url).content
    
    # opens a new file called avatar_img.png that will store the data's content
    f = open(f'{outdir}/avatar_img.png', 'wb')
    f.write(data)
    f.close

    img = Image.open(f'{outdir}/avatar_img.png')
    datas = img.getdata()

    # stores data for new image
    new_datas = []

    # updates image to make transparent background white
    for item in datas:
        if item[3] == 0:
            new_datas.append((255, 255, 255))
        else:
            new_datas.append(item)
    
    img.putdata(new_datas)
    img.save(f'{outdir}/avatar_img.png', 'PNG')

    img = cv2.imread(f'{outdir}/avatar_img.png')

    # resize image if needed to match scaling of other generated animations
    if np.max(img.shape) > 1000:
        scale = 1000 / np.max(img.shape)
        img = cv2.resize(img, (round(scale * img.shape[1]), round(scale * img.shape[0])))
    
    cropped = img[31: 950, 145: 474]
    cv2.imwrite(f'{outdir}/cropped_original_avatar_img.png', cropped)

    # delete the generated image
    os.remove(f'{outdir}/avatar_img.png')

    cropped_img = Image.open(f'{outdir}/cropped_original_avatar_img.png')

    # coordinates of mouth locations
    coordinate_list = [(109, 275), (122, 284), (110, 276), (109, 276), (109, 276), (109, 280), (112, 280)]

    # overlays each face shape onto avatar image
    for i in range(7):
        copied_img = cropped_img.copy()
        shape_img = Image.open('frontal_mouth_shapes/asset_' + str(i+1) + '.png')
        copied_img.paste(shape_img, coordinate_list[i], shape_img)
        copied_img.save(f'{outdir}/image_{i+1}.png')

    # generates gif
    make_gif(outdir)

def make_gif(frames_path):
    frames = [Image.open(image) for image in frames_path.glob('*')]
    frame_one = frames[0]

    # saves the talkign gif in the previously created directory
    frame_one.save(f'{frames_path}/talking.gif', format='GIF', append_images=frames, save_all=True, duration=100, loop=0)

if __name__ == '__main__':
    log_dir = Path('./logs')
    log_dir.mkdir(exist_ok=True, parents=True)
    logging.basicConfig(filename=f'{log_dir}/log.txt', level=logging.DEBUG)

    url = sys.argv[1]
    out_dir = sys.argv[2]

    generate_talking_animations(url, out_dir)

