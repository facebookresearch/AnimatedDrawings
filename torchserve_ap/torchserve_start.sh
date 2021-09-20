#!/bin/zsh

source /home/model-server/conda/etc/profile.d/conda.sh

conda activate alphapose

cd /home/model-server/torchserve_ap

torchserve --start --model-store model_store --models alphapose.mar --ts-config config.properties