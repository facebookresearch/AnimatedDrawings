import os, sys
import logging
from flask import Flask, make_response, request
import s3_object
import storage_service
import uuid



interim_store = storage_service.get_interim_store()
# video_store = storage_service.get_video_store()


app = Flask(__name__)




@app.route('/healthy', methods=['POST', 'HEAD', 'GET'])
def healthy():
	
    return {'message': 'Healthy'} 
   

@app.route('/clone_animation_iterim_files', methods=['POST'])
def clone_():
    """ Expects a POST with two fields:
     src_uuid: the UUID of an existing animation set. 
     dest_uuid: the new animation to clone

     curl -X POST -F 'src_uuid=123' -F 'dest_uuid=456' http://localhost:5000/clone_animation_iterim_files

     returns dest_uuid if everything is okay, 1 if anything failed
    """
    src_uuid = request.form['src_uuid']
    dest_uuid =  request.form.get('dest_uuid')

    assert  interim_store.exists(src_uuid, "image.png") , f'bad uuid {src_uuid}' # uuid is invalid
    
    try:
        if dest_uuid is None:
            dest_uuid = uuid.uuid4().hex 
        interim_store.clone(src_uuid, dest_uuid)

        return make_response(dest_uuid, 200)

    except Exception as e:
        # app.logger.exception('Failed to generate animation for uuid: %s', src_uuid)
        # app.log_exception(e)
        return make_response("1", 500)

