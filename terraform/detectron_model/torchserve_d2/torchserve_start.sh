#!/bin/bash

# source /home/model-server/conda/etc/profile.d/conda.sh

# conda activate detectron2

cd /home/model-server/torchserve_d2


ls
#torchserve --start --model-store /home/model-server/model_store --models D2_humanoid_detector.mar --ts-config config.properties --log-config log4j.properties --foreground


torchserve --start --model-store /home/model-server/torchserve_d2/ --models D2_humanoid_detector.mar --ts-config config.properties --log-config log4j.properties --foreground