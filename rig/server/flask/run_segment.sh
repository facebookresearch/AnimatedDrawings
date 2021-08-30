#!/bin/zsh

set -e
set -x

UUID=${1}
OUTPUT_PARENT_DIR='/private/home/hjessmith/flask/output_predictions/'${UUID}

source ~/.bashrc

########## Segment ##########
conda activate detectron2-2
 
python scripts/segment_mask.py ${OUTPUT_PARENT_DIR}
 
conda deactivate
