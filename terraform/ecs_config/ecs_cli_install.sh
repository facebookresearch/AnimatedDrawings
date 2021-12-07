#!/bin/bash

sudo curl -Lo /usr/local/bin/ecs-cli https://amazon-ecs-cli.s3.amazonaws.com/ecs-cli-linux-amd64-latest
gpg --import
curl -Lo ecs-cli.asc https://amazon-ecs-cli.s3.amazonaws.com/ecs-cli-linux-amd64-latest.asc
gpg --verify ecs-cli.asc /usr/local/bin/ecs-cli
sudo chmod +x /usr/local/bin/ecs-cli
ecs-cli --version