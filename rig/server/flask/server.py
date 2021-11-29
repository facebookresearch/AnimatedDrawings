from pathlib import Path
from flask import Flask, send_file, send_from_directory, flash, request, redirect, url_for, make_response
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
import os
import io
import subprocess
import json
import uuid
import shutil
import time
import logging
import requests
import base64
import cv2

import detect_humanoids
import detect_pose
import crop_from_bb
import segment_mask
import prep_animation_files
import s3_object

import storage_service


ANIMATION_ENDPOINT = os.environ.get("ANIMATION_ENDPOINT")


video_store = storage_service.get_video_store()
interim_store = storage_service.get_interim_store()
consent_store = storage_service.get_consent_store()



UPLOAD_FOLDER='./uploads/'
ALLOWED_EXTENSIONS= {'png'}


app = Flask(__name__)
gunicorn_logger = logging.getLogger('gunicorn.error')


if gunicorn_logger:
    root_logger = logging.getLogger()
    root_logger.handlers = gunicorn_logger.handlers
    root_logger.setLevel(gunicorn_logger.level)
cors = CORS(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CORS_HEADERS'] = 'Content-Type'

output_prediction_parent_dir = './output_predictions'

##############################################
# HTML form templates
##############################################
resource_request_form = '''<!doctype html>
    <title>Get {resource_type}</title>
    <h1>Get {resource_type}</h1>
    <p>Instructions:
        <ul>
            <li> Send the UUID of a previously uploaded image to server, get back the {resource_type}.</li> 
        </ul>
    </p>
    <form method=post enctype=multipart/form-data>
        <input type="text" name="uuid">
    <input type="submit" value="Upload">
    </form>
    '''

resource_set_form = '''<!doctype html>
    <title>Set {resource_type}</title>
    <h1>Set {resource_type}</h1>
    <p>Instructions:
        <ul>
            <li> Send the UUID of a previously uploaded image to server, along with new {resource_type}, to update {resource_type}.</li> 
        </ul>
    </p>
    <form method=post enctype=multipart/form-data>
        <input type="text" name="uuid">
        <input type="{input_type}" name="{resource_name}">
    <input type="submit" value="Upload">
    </form>
    '''
    
@app.route('/healthy', methods=['POST', 'HEAD', 'GET'])
def healthy():
	
    return {'message': 'Healthy'} 

##############################################
# initial image upload call
##############################################
@app.route('/upload_image', methods=['POST'])
@cross_origin()
def upload_image():
    """ Expects a POST request with a png image (request.files['file']). Returns a unique id that can be used to reference it in the future."""
    

    upload_enabled = os.environ.get("ENABLE_UPLOAD")
    if upload_enabled is None or upload_enabled != '1':
        return make_response("Uploading Images is currently forbidden", 403)


    file = request.files['file']

    unique_id = uuid.uuid4().hex

    interim_store.write_bytes(unique_id, "image.png", file.read())

    print(unique_id)
    
    detect_humanoids.detect_humanoids(unique_id)

    crop_from_bb.crop_from_bb(unique_id)

    return make_response(unique_id, 200)


##############################################
# if demo is being abused, we won't allow users to upload image, only go through process
# with a copy of a preapproved image. In that case, this function is called in place of upload_image()
##############################################
@app.route('/copy_preapproved_image', methods=['POST'])
@cross_origin()
def copy_preapproved_image():
    """ Expects a POST request with a string identifying the preapproved_image to copy (request.form['image_name']).
    Creates a copy of the image, returns a unique id that can be used to reference it in the future."""
    img_name = request.form['image_name']
    if img_name not in ['example3.png', 'example4.jpg', 'example5.png', 'example6.png']:
        return make_response(f"image name not in preapproved image names: {img_name}", 500)

    unique_id = uuid.uuid4().hex
    # #work_dir = os.path.join(app.config['UPLOAD_FOLDER'], unique_id)  #: remove this after switching to S3
    # #os.makedirs(work_dir, exist_ok=False)  # : remove this after switching to S3
    # s3_object.write_object(unique_id, "", "")


    ## ** verify whats going on here
    # TODO Read the pre-approved image an kick off workflow
    
    src = f'./preapproved_imgs/{img_name}'
    s3_object.write_object("/preapproved_imgs/", img_name)
    
    
    #dst = os.path.join(work_dir, 'image.png')  # TODO: remove this after switching to S3
    #shutil.copy(src, dst)  # TODO: replace this with call to S3 once Chris's changes have been merged

    detect_humanoids.detect_humanoids(unique_id)

    crop_from_bb.crop_from_bb(unique_id)

    return make_response(unique_id, 200)

##############################################
# At the request of upper management, adding in this function to run the entire pipeline
# Checks will be done for each step and, if all checks pass, an animation will be returned.
# If any of the checks fail, we will return the UUID of the image and should redirect the user to the first
# annotation page.
##############################################
@app.route('/run_full_pipeline', methods=['POST'])
@cross_origin()
def run_full_pipeline():
    """ Expects a POST request with a png image (request.files['file']). Returns video if all checks pass,
    returns the unique_id of image if a check fails."""
    file = request.files['file']

    unique_id = uuid.uuid4().hex
    interim_store.write_bytes(unique_id, "image.png", file)


    detect_humanoids.detect_humanoids(unique_id)
    if False:  # if failed the detection step
        return make_response(unique_id, 200)

    crop_from_bb.crop_from_bb(unique_id)

    detect_pose.detect_pose(unique_id)
    if False:  # if failed the pose detection step
        return make_response(unique_id, 200)

    segment_mask.segment_mask(unique_id)
    if False:  # if failed the segmentation step
        return make_response(unique_id, 200)


    prep_animation_files.prep_animation_files(unique_id)

    default_animation_type='running_jump'
    data = {"uuid": unique_id, "animation_type": default_animation_type}
    requests.post(url="http://animation_server:5000/generate_animation", data=data)

    # which function needs the url of the mp4 file
    # TODO at some point we need to return just the url of mp4 file. Not the whole file


    video_bytes = video_store.read_bytes(unique_id, f'{default_animation_type}.mp4')

    io_buf = io.BytesIO(video_bytes)
    return send_file(io_buf, download_name=f'{default_animation_type}.mp4')

##############################################
# set and get bounding box
##############################################
@app.route('/get_bounding_box_coordinates', methods=['GET', 'POST'])
@cross_origin()
def get_bounding_box_coordinates():
    """ Expects a POST request with a pre-existing uuid in accompanying form (request.form['uuid']). Returns the bounding box in json format"""
    if request.method != 'POST':
        return  resource_request_form.format(resource_type='Bounding Box Coordinates')

    unique_id = request.form['uuid']

    bb = interim_store.read_bytes(unique_id, "bb.json")
    return make_response(bb, 200)


@app.route('/set_bounding_box_coordinates', methods=['GET', 'POST'])
@cross_origin()
def set_bounding_box_coordinates():
    """ Expects a POST request with a pre-existing uuid in accompanying form (request.form['uuid']) and a valid bounding box json(request.form['bounding_box_coordinates']).
    Overwrites existing bounding box json and returns the new json"""
    if request.method != 'POST':
        return resource_set_form.format(
                resource_type='Bounding Box Coordinates',
                input_type='text',
                resource_name='bounding_box_coordinates'
                )

    unique_id = request.form['uuid']
    interim_store.write_bytes(unique_id, "bb.json", "")
    if interim_store.exists(unique_id, "bb.json") == False:
        return redirect(request.url)


    if interim_store.exists(unique_id, "bb.json") == True:
        bb = interim_store.read_bytes(unique_id, "bb.json")
        interim_store.write_bytes(unique_id, f"bb-{time.time()}.json", bb)

    interim_store.write_bytes(unique_id, "bb.json", request.form['bounding_box_coordinates'])



    crop_from_bb.crop_from_bb(unique_id)

    segment_mask.segment_mask(unique_id)

    # TODO @Jesse do we need to do this here? 
    detect_pose.detect_pose(unique_id)

    bb = interim_store.read_bytes(unique_id, "bb.json")
    return make_response(bb, 200)
##############################################


##############################################
# set and get mask
##############################################
@app.route('/get_mask', methods=['GET', 'POST'])
@cross_origin()
def get_mask():
    """ Expects a POST request with a pre-existing uuid in accompanying form (request.form['uuid']). Returns the segmentation mask as a RBG png"""
    if request.method != 'POST':
        return resource_request_form.format(resource_type='Mask')
    
    unique_id = request.form['uuid']
    if interim_store.exists(unique_id, "mask.png") == False:
        return redirect(request.url)
    mask =  storage_service.png_bytes_to_np(interim_store.read_bytes(unique_id, "mask.png"))
    _, buf = cv2.imencode('.png', mask)
    io_buf = io.BytesIO(buf)
    return send_file(io_buf, download_name='mask.png')

@app.route('/set_mask', methods=['GET', 'POST'])
@cross_origin()
def set_mask():
    """ Expects a POST request with a pre-existing uuid in accompanying form (request.form['uuid']) and a valid segmentation mask(request.files['file']).
    Overwrites existing segmentation mask and returns the new mask"""
    if request.method != 'POST':
        return resource_set_form.format(
                resource_type='Mask',
                input_type='file',
                resource_name='file'
                )
    unique_id = request.form['uuid']
    if interim_store.exists(unique_id, "mask.png") == False:
        return redirect(request.url)

    file = request.files['file']
    if file and allowed_file(file.filename):
        segment_mask.process_user_uploaded_segmentation_mask(unique_id, file)


    #return send_from_directory(work_dir, 'mask.png')
    mask = storage_service.png_bytes_to_np(interim_store.read_bytes(unique_id, "mask.png"))
    _, buf = cv2.imencode('.png', mask)
    io_buf = io.BytesIO(buf)
    return send_file(io_buf, download_name='mask.png')
##############################################


##############################################
# set and get joint locations
##############################################
@app.route('/get_joint_locations_json', methods=['GET', 'POST'])
@cross_origin()
def get_joint_locations():
    """ Expects a POST request with a pre-existing uuid in accompanying form (request.form['uuid']). Returns the joint_locations.json"""
    if request.method != 'POST':
        return resource_request_form.format(resource_type='Joint Locations JSON')
    
    unique_id = request.form['uuid']

    if interim_store.exists(unique_id, "joint_locations.json") == False:
        return redirect(request.url)
    
    joint_locations = interim_store.read_bytes(unique_id, "joint_locations.json")
    return joint_locations 

@app.route('/set_joint_locations_json', methods=['GET', 'POST'])
@cross_origin()
def set_joint_locations():
    """ Expects a POST request with a pre-existing uuid in accompanying form (request.form['uuid']) and a valid json with updated joint locations (request.form['joint_location_json']).
    Overwrites existing joint_locations.json and returns the new json"""
    unique_id = request.form['uuid']
    if request.method != 'POST':
        return resource_set_form.format(
                resource_type='Joint Locations JSON',
                input_type='text',
                resource_name='joint_location_json'
                )

    if interim_store.exists(unique_id, "joint_locations.json") == False:
        return redirect(request.url)

    if interim_store.exists(unique_id, "joint_locations.json") == True:
        joint_locations = interim_store.read_bytes(unique_id, "joint_locations.json")
        interim_store.write_bytes(unique_id, f"joint_locations-{time.time()}.json", joint_locations)

    interim_store.write_bytes(unique_id, "joint_locations.json", request.form['joint_location_json'])


    prep_animation_files.prep_animation_files(unique_id)

    joint_locations = interim_store.read_bytes(unique_id, "joint_locations.json")
    return joint_locations 
##############################################


##############################################
# misc getter functions
##############################################
@app.route('/get_image', methods=['GET', 'POST'])
@cross_origin()
def get_image():
    """ Expects a POST request with a pre-existing uuid in accompanying form (request.form['uuid']). Returns the original, full size image associated with that uuid"""
    unique_id = request.form['uuid']
    if request.method != 'POST':
        return resource_request_form.format('Full Image')

    if interim_store.exists(unique_id, "image.png") == False:
        return redirect(request.url)
    img_path = interim_store.read_bytes(unique_id, "image.png")
    return img_path


@app.route('/get_cropped_image', methods=['GET', 'POST'])
@cross_origin()
def get_cropped_image():
    """ Expects a POST request with a pre-existing uuid in accompanying form (request.form['uuid']). Returns the cropped_image.png, a version of the original image cropped to include only the character"""
    if request.method != 'POST':
        return  resource_request_form.format(resource_type='Cropped Image')

    unique_id = request.form['uuid']    
    if interim_store.exists(unique_id, "cropped_image.png") == False:
        return redirect(request.url)

    cropped_image = interim_store.read_bytes(unique_id, "cropped_image.png")
    return cropped_image

@app.route('/get_animation', methods=['GET', 'POST'])
@cross_origin()
def get_animation():
    """ Expects a POST request with a pre-existing uuid in accompanying form (request.form['uuid']), as well as an a string specifying the motion within the animation (request.form['animation']).
    Currently, supports 32 types of animations, but others may be added later. Returns the mp4 video of that character doing the requested motion"""
    if request.method != 'POST':
        return resource_set_form.format(resource_type='Animation', input_type='text', resource_name='animation')

    unique_id = request.form['uuid']
    if interim_store.exists(unique_id, "image.png") == False:
        return redirect(request.url)

    ### record annotations if consent is given ###
    #with open(os.path.join(work_dir, 'consent_response.txt'), 'r') as f:
    #    consent_response = bool(int(f.read(1)))  # file contains 0 if consent not given, 1 if consent given
    consent_response = bool(int(consent_store.read_bytes(unique_id, "consent_response.txt")))

    #TODO: @Chris, can you write us a function in s3_object to copy a subdirectory from one S3 bucket to another?
    # e.g. copy <ITERIM_S3_BUCKET>/<uuid> subdir and contents to <CONSENT_GIVEN_S3_BUCKET>/<uuid>? That needs to occur here.
    if consent_response:
        assert False
        # src = work_dir
        # dst = os.path.join(CONSENT_GIVEN_SAVE_DIR, unique_id)

        # if os.path.isdir(dst):
        #     shutil.rmtree(dst)

        # shutil.copytree(src, dst)


    animation_type = request.form['animation']

    assert animation_type in [
        'box_jump',
        'boxing',
        'catwalk_walk',
        'dab_dance',
        'dance',
        'dance001',
        'dance002',
        'floating',
        'flying_kick',
        'happy_idle',
        'hip_hop_dancing',
        'hip_hop_dancing2',
        'hip_hop_dancing3',
        'jab_cross',
        'joyful_jump_l',
        'jump',
        'jump_attack',
        'jump_rope',
        'punching_bag',
        'run',
        'run_walk_jump_walk',
        'running_jump',
        'shoot_gun',
        'shuffle_dance',
        'skipping',
        'standard_walk',
        'walk_punch_kick_jump_walk',
        'walk_sway',
        'walk_swing_arms',
        'wave_hello_3',
        'waving_gesture',
        'zombie_walk'], f'Unsupposed animation_type:{animation_type}'



    
    #cmd = f"curl -X POST -F uuid={unique_id} -F animation_type={animation_type} {ANIMATION_ENDPOINT}"
    #response = str(subprocess.check_output(cmd.split(' ')))

    data = {'uuid':unique_id, 'animation_type':animation_type}
    response = requests.post(url=ANIMATION_ENDPOINT, data=data)
    
    video_id = response.text
    # TODO at some point we need to return just the url of mp4 file. Not the whole file
    video_bytes = video_store.read_bytes(video_id, f'{animation_type}.mp4')
    io_buf = io.BytesIO(video_bytes)
    return send_file(io_buf, download_name=f'{animation_type}.mp4')




@app.route('/set_consent_answer', methods=['POST'])
@cross_origin()
def set_consent_answer():
    """Expects a POST request wiht a pre-existing uuid in accompanying form (request.form['uuid]) and a valid 'consent_response' (request.form['consent_response']).
        Contents of consent_response are:
            request.form['consent_response']== 1 if consent IS given to use image in training data and open source dataset
            request.form['consent_response']== 0 if consent IS NOT given to use image in training data and open source dataset

    Contents of consent_response will be written into the images work_dir, and later scripts will reference it when deciding whether to include it in future training data/ datasets.
    """


    # TODO uncomment this after calls to set_consent_answer and upload_image are reversed
    unique_id = request.form['uuid']
    consent_response = request.form['consent_response']
    consent_store.write_bytes(unique_id, 'consent_response.txt', consent_response)
    return make_response("", 200)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
        



##############################################
# old endpoing used MVP demo client
##############################################
@app.route('/upload', methods=['GET', 'POST'])
@cross_origin()
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            subprocess.run(['./old_mvp_run_pipeline.sh', filename], capture_output=True)
            return redirect(f'/result/{filename}')

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <p>Instructions:
        <ul>
            <li> Upload a .png file with a single drawn humanoid figure within it. </li> 
            <li> Wait ~45 seconds for video to be rendered and returned.</li>
            <li> If this page is reloaded, try with a different image (still under development). </li>
        </ul>
    </p>
    <form method=post enctype=multipart/form-data>
        <input type=file name=file>
    <input type=submit value=Upload>
    </form>
    '''

@app.route('/result/<name>')
def return_results(name):
    return send_from_directory('opengl_dev', 'out.mp4')
    #return send_from_directory(f'input_parent_dir/cropped_detections/composite_mask/', name)


##############################################
# Static web content
##############################################
resource_dir: Path = (Path(__file__).parent / "static").absolute()

@app.route("/")
def index_resource():
    return send_file(resource_dir / "index.html")

@app.errorhandler(404)
def not_found(e):
    return send_file(resource_dir / "index.html")

@app.route("/about")
def about_route():
    return send_file(resource_dir / "index.html")

@app.route("/canvas")
def canvas_route():
    return send_file(resource_dir / "index.html")

@app.route("/share/<name>/<type>")
def share_route(name, type):
    return send_file(resource_dir / "index.html")

@app.route("/<path>")
def root_resource(path: str):
    return send_file(resource_dir / path)


@app.route("/static/css/<path>")
def css_resource(path: str):
    return send_file(resource_dir / "static/css/" / path)


@app.route("/static/js/<path>")
def js_resource(path: str):
    return send_file(resource_dir / "static/js/" / path)

@app.route("/static/media/<path>")
def media_resource(path: str):
    return send_file(resource_dir / "static/media/" / path)
