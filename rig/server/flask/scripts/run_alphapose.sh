#!/bin/zsh

set -e
set -x
set -u

PARENT_INDIR=${1}  

CONFIG=/home/model-server/rig/server/configs/pose_detection.yaml
CHECKPOINT=/home/model-server/models/alphapose_weights.pth

cd /home/model-server/AlphaPose

conda run -v -n alphapose python scripts/demo_inference.py --cfg ${CONFIG} --checkpoint ${CHECKPOINT} --indir ${PARENT_INDIR} --detfile /home/model-server/rig/server/flask/${PARENT_INDIR}/sketch-DET.json

mv /home/model-server/AlphaPose/examples/res/alphapose-results.json /home/model-server/rig/server/flask/${PARENT_INDIR}/alphapose_results.json
