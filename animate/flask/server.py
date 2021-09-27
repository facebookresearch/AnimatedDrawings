import os
from flask import Flask, make_response, request
from flask_cors import cross_origin
import subprocess

app = Flask(__name__)

VIDEO_SHARE_ROOT='/home/animation-server/animate/flask/videos'
UPLOAD_FOLDER='/home/animation-server/animate/flask/uploads'  # TODO change from uploads to upload

@app.route('/generate_animation', methods=['POST'])
@cross_origin()
def generate_animation():
    """ Expects a POST with two fields:
     uuid: the UUID of an uploaded sketch. Assumes all files needed for rigging character will be stored there.
     animation_type: the type of animation (or motion) to use

     curl -X POST -F 'uuid=123' -F 'animation_type=hip_hop_dancing' http://animation_server:5000/generate_animation

     returns 0 if everything is okay, 1 if anything failed
    """
    unique_id = request.form['uuid']
    animation_type = request.form['animation_type']

    work_dir = os.path.join(UPLOAD_FOLDER, unique_id)

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

    # if mirror_concat, we augment the video by mirroring and appending
    mirror_concat = animation_type in [
        'catwalk_walk',
        'run',
        'run_walk_jump_walk',
        'running_jump',
        'skipping',
        'standard_walk',
        'walk_punch_kick_jump_walk',
        'walk_sway',
        'walk_swing_arms',
        'zombie_walk']

    animation_path = os.path.join(VIDEO_SHARE_ROOT, unique_id, f'{animation_type}.mp4')

    try:
        if not os.path.exists(animation_path):
            with open('./err.txt', 'w') as err:
                subprocess.run(['./run_animate.sh', os.path.abspath(work_dir), animation_type, str(int(mirror_concat)), os.path.abspath(os.path.join(VIDEO_SHARE_ROOT, unique_id))], check=True, stderr=err)
        return make_response("0", 200)

    except:
        return make_response("1", 200)
