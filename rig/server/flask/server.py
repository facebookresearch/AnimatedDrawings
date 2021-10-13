from pathlib import Path
from flask import Flask, send_file, send_from_directory, flash, request, redirect, url_for, make_response
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
import os
import subprocess
import json
import uuid
import shutil
import time

import detect_humanoids
import detect_pose
import crop_from_bb
import segment_mask
import prep_animation_files

UPLOAD_FOLDER='./uploads/'
CONSENT_GIVEN_SAVE_DIR = './consent_given_upload_copies/'
#VIDEO_SHARE_ROOT='/app/out/public/videos'
VIDEO_SHARE_ROOT='./videos/'
ALLOWED_EXTENSIONS= {'png'}

app = Flask(__name__)
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

##############################################
# initial image upload call
##############################################
@app.route('/upload_image', methods=['GET', 'POST'])
@cross_origin()
def upload_image():
    """ Expects a POST request with a png image (request.files['file']). Returns a unique id that can be used to reference it in the future."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        unique_id = uuid.uuid4().hex
        work_dir = os.path.join(app.config['UPLOAD_FOLDER'], unique_id)
        os.makedirs(work_dir, exist_ok=False)

        file.save(os.path.join(work_dir, 'image.png'))

        detect_humanoids.detect_humanoids(work_dir)

        crop_from_bb.crop_from_bb(work_dir)

        return make_response(unique_id, 200)
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


##############################################
# set and get bounding box
##############################################
@app.route('/get_bounding_box_coordinates', methods=['GET', 'POST'])
@cross_origin()
def get_bounding_box_coordinates():
    """ Expects a POST request with a pre-existing uuid in accompanying form (request.form['uuid']). Returns the bounding box in json format"""
    if request.method != 'POST':
        return  resource_request_form.format(resource_type='Bounding Box Coordinates')

    bb_path = os.path.join(UPLOAD_FOLDER, request.form['uuid'], 'bb.json')
    if not os.path.exists(bb_path):
        return redirect(request.url)

    with open(bb_path, 'r') as f:
        bb = json.load(f)
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
    bb_path = os.path.join(UPLOAD_FOLDER, unique_id, 'bb.json')
    if not os.path.exists(bb_path):  # uuid is invalid
        return redirect(request.url)

    # back up the previous bounding box annotations
    if os.path.exists(bb_path):
        shutil.move(bb_path, f'{bb_path}.{time.time()}')

    with open(bb_path, 'w') as f:
        json.dump(json.loads(request.form['bounding_box_coordinates']), f)

    work_dir = os.path.join(app.config['UPLOAD_FOLDER'], unique_id)

    crop_from_bb.crop_from_bb(work_dir)

    segment_mask.segment_mask(work_dir)

    # TODO @Jesse do we need to do this here? 
    detect_pose.detect_pose(work_dir)

    with open(bb_path, 'r') as f:
        bb = json.load(f)
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
    mask_path = os.path.join(UPLOAD_FOLDER, request.form['uuid'], 'mask.png')
    if not os.path.exists(mask_path):
        return redirect(request.url)

    return send_from_directory(os.path.join(UPLOAD_FOLDER,  request.form['uuid']), 'mask.png')

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
    work_dir = os.path.join(app.config['UPLOAD_FOLDER'], request.form['uuid'])
    mask_path = os.path.join(work_dir, 'mask.png')
    if not os.path.exists(mask_path):
        return redirect(request.url)

    file = request.files['file']
    if file and allowed_file(file.filename):
        segment_mask.process_user_uploaded_segmentation_mask(work_dir, file)


    return send_from_directory(work_dir, 'mask.png')
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

    joint_locations_json_path = os.path.join(UPLOAD_FOLDER, request.form['uuid'], 'joint_locations.json')
    if not os.path.exists(joint_locations_json_path):
        return redirect(request.url)

    return send_from_directory(os.path.join(UPLOAD_FOLDER,  request.form['uuid']), 'joint_locations.json')

@app.route('/set_joint_locations_json', methods=['GET', 'POST'])
@cross_origin()
def set_joint_locations():
    """ Expects a POST request with a pre-existing uuid in accompanying form (request.form['uuid']) and a valid json with updated joint locations (request.form['joint_location_json']).
    Overwrites existing joint_locations.json and returns the new json"""
    if request.method != 'POST':
        return resource_set_form.format(
                resource_type='Joint Locations JSON',
                input_type='text',
                resource_name='joint_location_json'
                )

    work_dir = os.path.join(app.config['UPLOAD_FOLDER'], request.form['uuid'])
    joint_locations_json_path = os.path.join(work_dir, 'joint_locations.json')
    if not os.path.exists(joint_locations_json_path):  # uuid is invalid
        return redirect(request.url)

    # back up the previous joint locations
    if os.path.exists(joint_locations_json_path):
        shutil.move(joint_locations_json_path, f'{joint_locations_json_path}.{time.time()}')

    with open(joint_locations_json_path, 'w') as f:
        json.dump(json.loads(request.form['joint_location_json']), f)

    prep_animation_files.prep_animation_files(work_dir, VIDEO_SHARE_ROOT)
    #subprocess.run(['./run_prep_animation_files.sh', os.path.join(UPLOAD_FOLDER,  request.form['uuid'])], check=True, capture_output=True)

    return send_from_directory(work_dir, 'joint_locations.json')
##############################################


##############################################
# misc getter functions
##############################################
@app.route('/get_image', methods=['GET', 'POST'])
@cross_origin()
def get_image():
    """ Expects a POST request with a pre-existing uuid in accompanying form (request.form['uuid']). Returns the original, full size image associated with that uuid"""
    if request.method != 'POST':
        return resource_request_form.format('Full Image')
    image_path = os.path.join(UPLOAD_FOLDER, request.form['uuid'], 'image.png')
    if not os.path.exists(image_path):
        return redirect(request.url)

    return send_from_directory(os.path.join(UPLOAD_FOLDER,  request.form['uuid']), 'image.png')


@app.route('/get_cropped_image', methods=['GET', 'POST'])
@cross_origin()
def get_cropped_image():
    """ Expects a POST request with a pre-existing uuid in accompanying form (request.form['uuid']). Returns the cropped_image.png, a version of the original image cropped to include only the character"""
    if request.method != 'POST':
        return  resource_request_form.format(resource_type='Cropped Image')

    cropped_image_path = os.path.join(UPLOAD_FOLDER, request.form['uuid'], 'cropped_image.png')
    if not os.path.exists(cropped_image_path):
        return redirect(request.url)

    return send_from_directory(os.path.join(UPLOAD_FOLDER,  request.form['uuid']), 'cropped_image.png')


@app.route('/get_animation', methods=['GET', 'POST'])
@cross_origin()
def get_animation():
    """ Expects a POST request with a pre-existing uuid in accompanying form (request.form['uuid']), as well as an a string specifying the motion within the animation (request.form['animation']).
    Currently, supports 32 types of animations, but others may be added later. Returns the mp4 video of that character doing the requested motion"""
    if request.method != 'POST':
        return resource_set_form.format(resource_type='Animation', input_type='text', resource_name='animation')

    unique_id = request.form['uuid']
    work_dir = os.path.join(app.config['UPLOAD_FOLDER'], unique_id)
    if not os.path.exists(work_dir):  # invalid uuid
        return redirect(request.url)

    ### record annotations if consent is given ###
    with open(os.path.join(work_dir, 'consent_response.txt'), 'r') as f:
        consent_response = bool(int(f.read(1)))  # file contains 0 if consent not given, 1 if consent given

    # TODO: Fix so that, whenever user confirms joint locations, we then copy their annotations to a permanent location
    # whenever a video is returned, if user consented to terms we copy the work_dir to a permanent location
    if consent_response:
        src = work_dir
        dst = os.path.join(CONSENT_GIVEN_SAVE_DIR, unique_id)

        if os.path.isdir(dst):
            shutil.rmtree(dst)

        shutil.copytree(src, dst)


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


    #animation_path = os.path.join(VIDEO_SHARE_ROOT, unique_id, f'{animation_type}.mp4')

    # TODO @Jesse Should the url be passed in as a parameter to the docker image?
    cmd = f"curl -X POST -F uuid={unique_id} -F animation_type={animation_type} http://animation_server:5000/generate_animation"
    response = str(subprocess.check_output(cmd.split(' ')))

    # TODO at some point we need to return just the url of mp4 file. Not the whole file
    return send_from_directory(os.path.join(VIDEO_SHARE_ROOT, request.form['uuid']), f'{animation_type}.mp4',
                               as_attachment=True)
    # if response =="0":  #everything okay
    # else:  # something went wrong
    #     pass
    #     return make_response("something went wrong", 500)



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
    work_dir = os.path.join(app.config['UPLOAD_FOLDER'], unique_id)

    with open(os.path.join(work_dir, 'consent_response.txt'), 'w') as f:
        f.write(f'{consent_response}')

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
def canvas_route():
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
