#!/bin/zsh

set -e
set -x
set -u

PARENT_INDIR=${1}  

#CONFIG=/private/home/hjessmith/05-07-21-bicyclegantest/condition4/05-07-21-bgtest-condition4.yaml 
#CHECKPOINT=/private/home/hjessmith/05-07-21-bicyclegantest/condition4/exp_05-07-21-bgtest-condition4-05-07-21-bgtest-condition4.yaml/model_299.pth
CONFIG=/home/model-server/rig/server/configs/pose_detection.yaml
CHECKPOINT=/home/model-server/alphapose_weights.pth

cd /home/model-server/AlphaPose

conda run -v -n alphapose python scripts/demo_inference.py --cfg ${CONFIG} --checkpoint ${CHECKPOINT} --indir ${PARENT_INDIR} --detfile /home/model-server/rig/server/flask/${PARENT_INDIR}/sketch-DET.json

mv /home/model-server/AlphaPose/examples/res/alphapose-results.json /home/model-server/rig/server/flask/${PARENT_INDIR}/alphapose_results.json
