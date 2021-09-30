import os
from flask import Flask, make_response, request
from flask_cors import cross_origin
import subprocess

import sys
sys.path.insert(0, '..')
import sketch_animate.main_server

app = Flask(__name__)

VIDEO_SHARE_ROOT='/home/animation-server/animate/flask/videos'
UPLOAD_FOLDER='/home/animation-server/animate/flask/uploads'  # TODO change from uploads to upload

@app.route('/generate_animation', methods=['POST'])
def generate_animation():
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

    video_output_path = os.path.join(VIDEO_SHARE_ROOT, unique_id, f'{animation_type}.mp4')

    try:
        if not os.path.exists(video_output_path):
            motion_cfg_path = f'/home/animation-server/animate/Data/motion_configs/{animation_type}.yaml'
            character_cfg_path = f'{UPLOAD_FOLDER}/{unique_id}/animation/cropped_image.yaml'
            #os.makedirs(video_output_path, exist_ok=True)
            print('starting')
            sketch_animate.main_server.video_from_cfg(character_cfg_path, motion_cfg_path, video_output_path)
            #subprocess.run(['./run_animate.sh', os.path.abspath(work_dir), animation_type, str(int(mirror_concat)), os.path.abspath(os.path.join(VIDEO_SHARE_ROOT, unique_id))], check=True, stderr=err)
        return make_response("0", 200)

    except Exception as e:
        return make_response(str(e), 200)





    # video_output_path = '/home/animation-server/animate/flask/videos/0012950cbc2846c890ed6151a6e64d94/'
    # os.makedirs(video_output_path, exist_ok=True)
    # motion_cfg_path = '/home/animation-server/animate/Data/motion_configs/walk_sway.yaml'
    # character_cfg_path = '/home/animation-server/animate/flask/uploads/0012950cbc2846c890ed6151a6e64d94/animation/cropped_image.yaml'  # TODO change from uploads to upload
    # sketch_animate.main_server.video_from_cfg(character_cfg_path, motion_cfg_path, video_output_path)
    # return make_response("0", 200)
print('test')
@app.route('/generate_animation1', methods=['POST'])
@cross_origin()
def generate_animation1():
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

import logging

if 'SKETCH_ANIMATE_RENDER_BACKEND' in os.environ and \
        os.environ['SKETCH_ANIMATE_RENDER_BACKEND'] == 'OPENGL':
    logging.info('SKETCH_ANIMATE_RENDER_BACKEND == OPENGL. Using OpenGL')
    try:
        from OpenGL import GL
    except:
        logging.critical('Error initializing OpenGL. Aborting')
    logging.info('OpenGL successfully initialized')

else:
    logging.info('SKETCH_ANIMATE_RENDER_BACKEND != OPENGL, Using OSMesa')
    try:
        os.environ['PYOPENGL_PLATFORM'] = "osmesa"
        os.environ['MUJOCO_GL'] = "osmesa"
        os.environ['MESA_GL_VERSION_OVERRIDE'] = "3.3"
        from OpenGL import GL, osmesa
    except:
        logging.critical('Error initializing osmesa. Aborting')
    logging.info('osmesa successfully initialized')

print('test')


