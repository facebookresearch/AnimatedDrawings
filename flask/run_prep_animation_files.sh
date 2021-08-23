#!/bin/zsh

set -e
set -x

UUID=${1}
OUTPUT_PARENT_DIR='/private/home/hjessmith/flask/output_predictions/'${UUID}

source ~/.bashrc

########## Delete existing videos ##########
rm -rf ${OUTPUT_PARENT_DIR}/animation/wave.mp4
rm -rf ${OUTPUT_PARENT_DIR}/animation/dance.mp4
rm -rf ${OUTPUT_PARENT_DIR}/animation/run_jump.mp4

########## Prep Animation Files ##########
conda activate detectron2-2

python scripts/prep_animation_files.py ${OUTPUT_PARENT_DIR}

conda deactivate
