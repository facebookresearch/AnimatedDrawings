import os, sys
import logging
from flask import Flask, make_response, request
sys.path.insert(0, '..')
import sketch_animate.main_server

app = Flask(__name__)

gunicorn_logger = logging.getLogger('gunicorn.error')

if gunicorn_logger:
    root_logger = logging.getLogger()
    root_logger.handlers = gunicorn_logger.handlers
    root_logger.setLevel(gunicorn_logger.level)

VIDEO_SHARE_ROOT='./videos' # maps to /home/animation-server/animate/flask/videos
UPLOAD_FOLDER='./uploads' # /home/animation-server/animate/flask/uploads

@app.route('/generate_animation', methods=['POST'])
def generate_animation():
    """ Expects a POST with two fields:
     uuid: the UUID of an uploaded sketch. Assumes all files needed for rigging character will be stored there.
     animation_type: the type of animation (or motion) to use

     curl -X POST -F 'uuid=123' -F 'animation_type=hip_hop_dancing' http://animation_server:5000/generate_animation

     returns 0 if everything is okay, 1 if anything failed
    """
    unique_id = request.form['uuid']
    assert os.path.exists(os.path.join(UPLOAD_FOLDER, unique_id)), f'bad uuid {unique_id}' # uuid is invalid

    animation_type = request.form['animation_type']
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

    video_output_path = os.path.join(VIDEO_SHARE_ROOT, unique_id, f'{animation_type}.mp4')

    try:
        if not os.path.exists(video_output_path):
            motion_cfg_path = f'/home/animation-server/animate/Data/motion_configs/{animation_type}.yaml'
            character_cfg_path = f'{UPLOAD_FOLDER}/{unique_id}/animation/cropped_image.yaml'
            sketch_animate.main_server.video_from_cfg(character_cfg_path, motion_cfg_path, video_output_path)
        return make_response("0", 200)

    except Exception as e:
        app.logger.exception('Failed to generate animation for uuid: %s', unique_id)
        app.log_exception(e)
        return make_response("1", 500)

