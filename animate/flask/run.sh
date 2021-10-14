#!/bin/bash

#conda run -n sketch_animate gunicorn server:app -w 2 --threads 2 -b 0.0.0.0:5000 && tail -f error.log
# touch /home/animation-server/animate/flask/access.log
# touch /home/animation-server/animate/flask/error.log

# As per guidance from https://docs.docker.com/config/containers/logging/
# and https://github.com/nginxinc/docker-nginx/blob/8921999083def7ba43a06fabd5f80e4406651353/mainline/jessie/Dockerfile#L21-L23
# forward request and error logs to docker log collector
ln -sf /dev/stdout access.log \
	&& ln -sf /dev/stderr error.log

# TODO: following command is failing when run from docker-compose.yaml, but works when run from CL shell inside container
gunicorn server:app --access-logfile access.log --log-file error.log -w 2 --threads 2 -b 0.0.0.0:5000 ; tail -f error.log
