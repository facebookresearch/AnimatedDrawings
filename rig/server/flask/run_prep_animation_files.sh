#!/bin/zsh

set -e
set -x

WORK_DIR=${1}

#source ~/.bashrc

########## Delete existing videos ##########
rm -rf ${WORK_DIR}/animation/wave.mp4
rm -rf ${WORK_DIR}/animation/dance.mp4
rm -rf ${WORK_DIR}/animation/run_jump.mp4

########## Prep Animation Files ##########
# conda activate detectron2-2

conda run -n detectron2 python scripts/prep_animation_files.py ${WORK_DIR}

# conda deactivate
