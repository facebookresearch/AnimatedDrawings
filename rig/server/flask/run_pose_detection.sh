#!/bin/zsh

set -e
set -x

WORK_DIR=${1}

# ########### Run Alphapose ##########
./scripts/run_alphapose.sh ${WORK_DIR}

./scripts/alphapose_visualize.sh ${WORK_DIR}

python scripts/organize_joint_predictions.py ${WORK_DIR}
