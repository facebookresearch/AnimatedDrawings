#!/bin/zsh

source /home/model-server/conda/etc/profile.d/conda.sh

conda activate detectron2

cd /home/model-server/torchserve_d2

torchserve --start --model-store model_store --models D2_humanoid_detector.mar --ts-config config.properties
