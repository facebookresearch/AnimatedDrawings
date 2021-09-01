#!/bin/zsh

# source ~/.bashrc
# conda activate flask

# export FLASK_ENV=development
# #export FLASK_APP=server_dev
# export FLASK_APP=server

# flask run
conda run -n flask gunicorn server:app --access-logfile access.log --log-file error.log -w 2 --threads 2 -b 0.0.0.0:5000 && tail -f error.log
