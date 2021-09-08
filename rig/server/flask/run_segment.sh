#!/bin/zsh

set -e
set -x

UUID=${1}
OUTPUT_PARENT_DIR='output_predictions/'${UUID}

source ~/.bashrc

########## Segment ##########
# conda activate detectron2-2
 
conda run -n detectron2 python scripts/segment_mask.py ${OUTPUT_PARENT_DIR}
 
# conda deactivate
