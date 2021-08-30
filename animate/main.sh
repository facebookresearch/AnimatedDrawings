#!/bin/zsh

set -e
set -x

MOTION_CONFIG=${1}
CHARACTER_CONFIG=${2}

cd sketch_animate
python main.py ${MOTION_CONFIG} ${CHARACTER_CONFIG}

