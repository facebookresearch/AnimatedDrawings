#!/bin/zsh

set -e
set -x

UUID=${1}
OUTPUT_PARENT_DIR='/private/home/hjessmith/flask/output_predictions/'${UUID}

source ~/.bashrc

########### Run Detectron2 Humanoid Prediction ##########
conda activate detectron2-2

python scripts/detect-humanoids.py ${OUTPUT_PARENT_DIR}

conda deactivate
