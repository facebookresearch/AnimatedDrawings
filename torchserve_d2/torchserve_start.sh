#!/bin/bash

# source /home/model-server/conda/etc/profile.d/conda.sh

# conda activate detectron2

cd /home/model-server/torchserve_d2

# 
# Using Hamid's mar file from https://s3.us-west-2.amazonaws.com/ts0.4.1-marfiles/D2_humanoid_detector_gpu_half.mar

torchserve --start --model-store /home/model-server/torchserve_d2/ --models D2_humanoid_detector.mar --ts-config config.properties --log-config log4j.properties --foreground
