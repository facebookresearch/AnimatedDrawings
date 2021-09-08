#!/bin/zsh

# setup runtime env vars for react app
./env.sh
cp env-config.js static/
# start flask server
conda run -n flask gunicorn server:app --access-logfile access.log --log-file error.log -w 2 --threads 2 -b 0.0.0.0:5000 && tail -f error.log
