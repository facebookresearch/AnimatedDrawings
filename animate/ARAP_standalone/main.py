import glfw
import sys, os
from PIL import Image
from viewer import Viewer
from ARAP import ARAP


def get_image_and_mask(img_path, mask_path):
    try:
        img = Image.open(img_path)
    except:
        assert False, "Could not open image path: {}".format(img_path)

    try:
        mask = Image.open(mask_path)
    except:
        assert False, "Could not open mask path: {}".format(mask_path)

    assert mask.size == img.size, "Size of image and mask do not match"
    assert img.mode == 'RGB', "Image must be of type RGB"
    assert mask.mode == '1', "Mask must be of type '1'"

    return img, mask

if __name__ == '__main__':
    img_path = sys.argv[1]
    mask_path = sys.argv[2]
    img, mask = get_image_and_mask(img_path, mask_path)

    arap_handles_path = sys.argv[3]

    glfw.init()
    viewer = Viewer(*img.size)


    arap = ARAP(img, mask, arap_handles_path)

    viewer.add_arap(arap)
    viewer.run()

    glfw.terminate()
