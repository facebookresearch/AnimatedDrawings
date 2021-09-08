#!/bin/zsh

set -e
set -x

UUID=${1}
OUTPUT_PARENT_DIR='output_predictions/'${UUID}

# source ~/.bashrc

########### Crop bounding boxes##########
# conda activate detectron2-2

conda run -n detectron2 python scripts/crop_from_bb.py ${OUTPUT_PARENT_DIR}

# conda deactivate
