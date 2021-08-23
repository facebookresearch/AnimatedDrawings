from enum import Enum
from flask import Flask, send_file, send_from_directory, flash, request, redirect, url_for, make_response
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from markupsafe import escape
import os
import subprocess
import json
import uuid

UPLOAD_FOLDER='./uploads/'
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
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_id = uuid.uuid4().hex
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            subprocess.run(['./upload_image.sh', filename, unique_id], check=True)
            subprocess.run(['./run_detection.sh', unique_id], check=True)
            subprocess.run(['./run_crop.sh', unique_id], check=True)
            subprocess.run(['./run_segment.sh', unique_id], check=True)
            subprocess.run(['./run_pose_detection.sh', unique_id], check=True)
            subprocess.run(['./run_prep_animation_files.sh', unique_id], check=True)

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

    bb_path = os.path.join(output_prediction_parent_dir, request.form['uuid'], 'bb.json')
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
    bb_path = os.path.join(output_prediction_parent_dir, unique_id, 'bb.json')
    if not os.path.exists(bb_path):  # uuid is invalid
        return redirect(request.url)

    with open(bb_path, 'w') as f:
        json.dump(json.loads(request.form['bounding_box_coordinates']), f)

    subprocess.run(['./run_crop.sh', unique_id], check=True)
    subprocess.run(['./run_segment.sh', unique_id], check=True)
    subprocess.run(['./run_pose_detection.sh', unique_id], check=True)
    subprocess.run(['./run_prep_animation_files.sh', unique_id], check=True)

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
    mask_path = os.path.join(output_prediction_parent_dir, request.form['uuid'], 'mask.png')
    if not os.path.exists(mask_path):
        return redirect(request.url)

    return send_from_directory(os.path.join(output_prediction_parent_dir,  request.form['uuid']), 'mask.png')

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
    mask_path = os.path.join(output_prediction_parent_dir, unique_id, 'mask.png')
    if not os.path.exists(mask_path):
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(output_prediction_parent_dir, unique_id, 'mask.png'))

        subprocess.run(['./run_prep_animation_files.sh', unique_id], check=True)

    return send_from_directory(os.path.join(output_prediction_parent_dir,  unique_id), 'mask.png')
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

    joint_locations_json_path = os.path.join(output_prediction_parent_dir, request.form['uuid'], 'joint_locations.json')
    if not os.path.exists(joint_locations_json_path):
        return redirect(request.url)

    return send_from_directory(os.path.join(output_prediction_parent_dir,  request.form['uuid']), 'joint_locations.json')

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

    unique_id = request.form['uuid']
    joint_locations_json_path = os.path.join(output_prediction_parent_dir, unique_id, 'joint_locations.json')
    if not os.path.exists(joint_locations_json_path):  # uuid is invalid
        return redirect(request.url)

    with open(joint_locations_json_path, 'w') as f:
        json.dump(json.loads(request.form['joint_location_json']), f)

    subprocess.run(['./run_prep_animation_files.sh', unique_id], check=True)

    return send_from_directory(os.path.join(output_prediction_parent_dir,  unique_id), 'joint_locations.json')
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
    image_path = os.path.join(output_prediction_parent_dir, request.form['uuid'], 'image.png')
    if not os.path.exists(image_path):
        return redirect(request.url)

    return send_from_directory(os.path.join(output_prediction_parent_dir,  request.form['uuid']), 'image.png') 


@app.route('/get_cropped_image', methods=['GET', 'POST'])
@cross_origin()
def get_cropped_image():
    """ Expects a POST request with a pre-existing uuid in accompanying form (request.form['uuid']). Returns the cropped_image.png, a version of the original image cropped to include only the character"""
    if request.method != 'POST':
        return  resource_request_form.format(resource_type='Cropped Image')

    cropped_image_path = os.path.join(output_prediction_parent_dir, request.form['uuid'], 'cropped_image.png')
    if not os.path.exists(cropped_image_path):
        return redirect(request.url)

    return send_from_directory(os.path.join(output_prediction_parent_dir,  request.form['uuid']), 'cropped_image.png')


@app.route('/get_animation', methods=['GET', 'POST'])
@cross_origin()
def get_animation():
    """ Expects a POST request with a pre-existing uuid in accompanying form (request.form['uuid']), as well as an a string specifying the motion within the animation (request.form['animation']).
    Currently, should be 'run_jump', 'wave', 'dance', but others may be added later. Returns the mp4 video of that character doing the requested motion"""
    if request.method != 'POST':
        return resource_set_form.format(resource_type='Animation', input_type='text', resource_name='animation')

    unique_id = request.form['uuid']
    if not os.path.exists(os.path.join(output_prediction_parent_dir, request.form['uuid'])):  # invalid uuid
        return redirect(request.url)

    animation_type = request.form['animation']
    assert animation_type in ['run_jump', 'wave', 'dance']

    animation_path = os.path.join(output_prediction_parent_dir, request.form['uuid'], 'animation', f'{animation_type}.mp4')
    if not os.path.exists(animation_path):
        subprocess.run(['./run_animate.sh', unique_id, animation_type], check=True)

    return send_from_directory(os.path.join(output_prediction_parent_dir,  request.form['uuid'], 'animation'), f'{animation_type}.mp4', as_attachment=True)


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
            subprocess.run(['./old_mvp_run_pipeline.sh', filename])
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
