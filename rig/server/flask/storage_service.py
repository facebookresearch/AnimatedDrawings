import os
import numpy as np
import s3_object
import cv2

USE_AWS = os.environ.get("USE_AWS") == 1


class aws_storage_service:

    def __init__(self, root):
      self.store = s3_object.s3_object(root)

    def read_bytes(self, unique_id, file_name):
        # if USE_AWS
        return self.store.get_object_bytes(unique_id, file_name);


    def write_bytes(self, unique_id, file_name, bytes):
        # if USE_AWS
        return self.store.write_object(unique_id, file_name, bytes);


def get_interim_store():
    # TODO get bucket from from config
    # if USE_AWS:
        return aws_storage_service('dev-demo-sketch-out-interim-files')
    # else:
        # return file_storage_service('temp')


def np_to_png_bytes(DATA):
    assert type(DATA) == np.ndarray, f"DATA is not np array. is {type(DATA)}"
    _, buf = cv2.imencode('.png', DATA)
    return buf.tobytes()

def png_bytes_to_np(img_bytes):
    img_np = cv2.imdecode(np.asarray(bytearray(img_bytes)), 1)    
    return img_np
