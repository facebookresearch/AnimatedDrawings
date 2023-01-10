from flask import Flask
#from flask import Flask, make_response, request
#import logging


app = Flask(__name__)


@app.route('/image_to_animation', methods=['POST'])  #type: ignore
def image_to_animation():
    """
    An endpoint that attempts end-to-end animation generation given a single image.

    Expects:
        image: the image to extract a character from.
        bvh_metadata_cfg: a configuration file specifying details about the driving BVH
        char_bvh_retargeting_cfg: a configuation file specifying how the driving BVH should be applied to character
        char_skeleton_cfg: a configuration file specifying the skeletal type of the drawn character
        user_scene_config: Additional configuration files needed to set up and render the video

    Returns:
        On success: a video file containing the animation.
        On Failure: 500 error with failure description.
    """
    pass


@app.route('/image_to_predictions', methods=['POST'])  #type: ignore
def image_to_predictions():
    """
    Runs character detection, segmentation, and pose estimation on the character and returns the results.

    Expects: 
        image: the image to extract a character from.
        char_skeleton_cfg: a configuration file specifying the skeletal type of the drawn character. Currently only humanoid supported.

    Returns:
        Bounding box prediction
        Segmentation prediction
        Pose Detection Prediction
        Result visualization
    """
    pass


@app.route('image_plus_annotations_to_animation', methods=['POST'])  #type: ignore
def image_plus_annotations_to_animation():
    """
    Given an image, annotations, and appropriate configs, creates an animation.
    Expects: 
        image: the image to extract a character from.
        annotations: annotations in the form returned by image_to_predictions
        bvh_metadata_cfg: a configuration file specifying details about the driving BVH
        char_bvh_retargeting_cfg: a configuation file specifying how the driving BVH should be applied to character
        user_scene_config: Additional configuration files needed to set up and render the video

    Returns:
        On success: a video file containing the animation.
        On Failure: 500 error with failure description.

    predictions
    """
    pass
