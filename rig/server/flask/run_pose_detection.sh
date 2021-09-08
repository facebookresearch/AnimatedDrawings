#!/bin/zsh

set -e
set -x

UUID=${1}
OUTPUT_PARENT_DIR='output_predictions/'${UUID}

# ########### Run Alphapose ##########
./scripts/run_alphapose.sh ${OUTPUT_PARENT_DIR}

./scripts/alphapose_visualize.sh ${OUTPUT_PARENT_DIR}

python scripts/organize_joint_predictions.py ${OUTPUT_PARENT_DIR}
