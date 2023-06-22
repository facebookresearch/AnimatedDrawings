# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from PIL import Image, ImageOps
import numpy as np
import numpy.typing as npt
import cv2
from pathlib import Path
import logging
from pkg_resources import resource_filename

TOLERANCE = 10**-5


def resolve_ad_filepath(file_name: str, file_type: str) -> Path:
    """
    Given input filename, attempts to find the file, first by relative to cwd,
    then by absolute, the relative to animated_drawings root directory.
    If not found, prints error message indicating which file_type it is.
    """
    if Path(file_name).exists():
        return Path(file_name)
    elif Path.joinpath(Path.cwd(), file_name).exists():
        return Path.joinpath(Path.cwd(), file_name)
    elif Path(resource_filename(__name__, file_name)).exists():
        return Path(resource_filename(__name__, file_name))
    elif Path(resource_filename(__name__, str(Path('..', file_name)))):
        return Path(resource_filename(__name__, str(Path('..', file_name))))

    msg = f'Could not find the {file_type} specified: {file_name}'
    logging.critical(msg)
    assert False, msg


def read_background_image(file_name: str) -> npt.NDArray[np.uint8]:
    """
    Given path to input image file, opens it, flips it based on EXIF tags, if present, and returns image with proper orientation.
    """
    # Check the file path
    file_path = resolve_ad_filepath(file_name, 'background_image')

    # Open the image and rotate as needed depending upon exif tag
    image = Image.open(str(file_path))
    image = ImageOps.exif_transpose(image)

    # Convert to numpy array and flip rightside up
    image_np = np.asarray(image)
    image_np = cv2.flip(image_np, 0)

    # Ensure we have RGBA
    if len(image_np.shape) == 3 and image_np.shape[-1] == 3:  # if RGB
        image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2RGBA)
    if len(image_np.shape) == 2:  # if grayscale
        image_np = cv2.cvtColor(image_np, cv2.COLOR_GRAY2RGBA)

    return image_np.astype(np.uint8)
