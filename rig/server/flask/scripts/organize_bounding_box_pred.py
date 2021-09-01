import pickle
from pathlib import Path
import os
import detectron2
import uuid
import sys
import shutil
sys.path.insert(0, '/private/home/hjessmith/utils_j')
import d2prediction_utils as d2p
import json

upload_fn = sys.argv[1]
d2_output_dir = sys.argv[2]
unique_id = sys.argv[3]
output_parent_dir = '/private/home/hjessmith/flask/output_predictions'
input_parent_dir = f'/private/home/hjessmith/flask/output_predictions/{unique_id}/input_parent_dir/input/image'

# get bounding box
pred_pickle = os.path.join(d2_output_dir, Path(upload_fn).stem + '.pickle')
with open(pred_pickle, 'rb') as f:
    data = pickle.load(f)
    bb = d2p.get_bb_from_multiple_bb(data, 25)

output_dir = os.path.join(output_parent_dir, unique_id)

# move original image
src = os.path.join(input_parent_dir, upload_fn)
dst = os.path.join(output_dir, 'image.png')
shutil.copy(src, dst)

# move d2 visualization image
src = os.path.join(d2_output_dir, upload_fn)
dst = os.path.join(output_dir, 'd2_viz.png')
shutil.copy(src, dst)

# move bounding box coordinates
with open(os.path.join(output_dir, 'bb.json'), 'w') as f:
    json.dump(bb, f)






