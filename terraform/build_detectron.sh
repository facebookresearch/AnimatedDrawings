#!/bin/bash


ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

ECR_ARN=$(terraform output --json  | jq -r .detectron_ecr_arn.value)
CONTAINER_NAME=$(terraform output --json | jq -r .detectron_container_name.value)
REGION=$(curl -s http://169.254.169.254/latest/dynamic/instance-identity/document|jq -r .region)

aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.us-east-2.amazonaws.com



DOCKER_BUILDKIT=1 docker build -t $CONTAINER_NAME:lastest -f /sketch_rig/Dockerfile.detectron_runtime .
docker tag $CONTAINER_NAME:lastest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$CONTAINER_NAME:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$CONTAINER_NAME:latest



#DOCKER_BUILDKIT=1 docker build -t detectron2_runtime:latest -f Dockerfile.detectron_runtime .
#docker tag detectron2_runtime:latest 790537050551.dkr.ecr.us-east-2.amazonaws.com/detectron2_runtime
#docker push 790537050551.dkr.ecr.us-east-2.amazonaws.com/detectron2_runtime