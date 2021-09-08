#!/bin/zsh

set -e
set -x

UUID=${1}
OUTPUT_PARENT_DIR='output_predictions/'${UUID}

# source ~/.bashrc

########### Run Detectron2 Humanoid Prediction ##########
# conda activate detectron2-2

conda run -v -n detectron2 python scripts/detect-humanoids.py ${OUTPUT_PARENT_DIR} 

# conda deactivate
