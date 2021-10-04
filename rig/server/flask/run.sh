#!/bin/bash



# setup runtime env vars for react app
./env.sh
cp env-config.js static/
# start flask server

tail -f error.log & 
gunicorn server:app --access-logfile access.log --log-file error.log -w 5 --threads 5 -b 0.0.0.0:5000 ; cat error.log
