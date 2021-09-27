#!/bin/bash

#conda run -n sketch_animate gunicorn server:app -w 2 --threads 2 -b 0.0.0.0:5000 && tail -f error.log
touch /home/animation-server/animate/flask/access.log
touch /home/animation-server/animate/flask/error.log

# TODO: following command is failing when run from docker-compose.yaml, but works when run from CL shell inside container
conda run -n sketch_animate gunicorn server:app --access-logfile /home/animation-server/animate/flask/access.log --log-file /home/animation-server/animate/flask/error.log -w 2 --threads 2 -b 0.0.0.0:5000 && tail -f error.log


sleep infinity