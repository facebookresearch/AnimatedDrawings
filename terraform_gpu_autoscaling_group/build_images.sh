#!/bin/bash

# Set ACCOUNT_ID and REGION variables 
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=$(curl -s http://169.254.169.254/latest/dynamic/instance-identity/document|jq -r .region)


# Set DETECTRON_ECR and DETECTRON_CONTAINER_NAME
DETECTRON_GPU_ECR=$(terraform output --json  | jq -r .detectron_gpu_ecr.value)
DETECTRON_GPU_CONTAINER_NAME=$(terraform output --json | jq -r .detectron_gpu_container_name.value)

# Authenticate into ECR
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.us-east-2.amazonaws.com

# Push and Build Detectron Image
DOCKER_BUILDKIT=1 docker build -t $DETECTRON_GPU_CONTAINER_NAME:latest  -f ../Dockerfile.detectron-gpu ..
docker tag $DETECTRON_GPU_CONTAINER_NAME:latest $DETECTRON_GPU_ECR
docker push $DETECTRON_GPU_ECR:latest
