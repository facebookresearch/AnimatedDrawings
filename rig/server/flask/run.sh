#!/bin/zsh

# start torchserve for detectron2 model in background
/home/model-server/torchserve_d2/torchserve_start.sh &

# setup runtime env vars for react app
./env.sh
cp env-config.js static/
# start flask server
conda run -n flask gunicorn server:app --access-logfile access.log --log-file error.log -w 5 --threads 5 -b 0.0.0.0:5000 && tail -f error.log
