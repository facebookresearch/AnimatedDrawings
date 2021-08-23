#!/bin/zsh

source ~/.bashrc
conda activate flask

export FLASK_ENV=development
#export FLASK_APP=server_dev
export FLASK_APP=server

flask run
