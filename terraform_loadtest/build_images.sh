#!/bin/bash

# Set ACCOUNT_ID and REGION variables 
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=$(curl -s http://169.254.169.254/latest/dynamic/instance-identity/document|jq -r .region)

# Set DETECTRON_ECR and DETECTRON_CONTAINER_NAME
DETECTRON_ECR=$(terraform output --json  | jq -r .detectron_ecr.value)
DETECTRON_CONTAINER_NAME=$(terraform output --json | jq -r .detectron_container_name.value)


# Set DETECTRON_ECR and DETECTRON_CONTAINER_NAME
DETECTRON_GPU_ECR=$(terraform output --json  | jq -r .detectron_gpu_ecr.value)
DETECTRON_GPU_CONTAINER_NAME=$(terraform output --json | jq -r .detectron_gpu_container_name.value)


# Set ALPHAPOSE_ECR and ALPHAPOSE_CONTAINER_NAME
#ALPHAPOSE_ECR=$(terraform output --json  | jq -r .alphapose_ecr.value)
#ALPHAPOSE_CONTAINER_NAME=$(terraform output --json | jq -r .alphapose_container_name.value)

# Set ANIMATION_ECR and ANIMATION_CONTAINER_NAME
#ANIMATION_ECR=$(terraform output --json  | jq -r .animation_ecr.value)
#ANIMATION_CONTAINER_NAME=$(terraform output --json | jq -r .animation_container_name.value)

# Set SKETCH_ECR and SKETCH_CONTAINER_NAME
#SKETCH_ECR=$(terraform output --json  | jq -r .sketch_ecr.value)
#SKETCH_CONTAINER_NAME=$(terraform output --json | jq -r .sketch_container_name.value)

# Authenticate into ECR
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.us-east-2.amazonaws.com

# Push and Build Detectron Image
#DOCKER_BUILDKIT=1 docker build -t $DETECTRON_CONTAINER_NAME:latest  -f ../Dockerfile.detectron_prod ..
#docker tag $DETECTRON_CONTAINER_NAME:latest $DETECTRON_ECR
#docker push $DETECTRON_ECR:latest


# Push and Build Detectron Image
DOCKER_BUILDKIT=1 docker build -t $DETECTRON_GPU_CONTAINER_NAME:latest  -f ../Dockerfile.detectron-gpu ..
docker tag $DETECTRON_GPU_CONTAINER_NAME:latest $DETECTRON_GPU_ECR
docker push $DETECTRON_GPU_ECR:latest

# Push and Build Alphapose Image
#DOCKER_BUILDKIT=1 docker build -t $ALPHAPOSE_CONTAINER_NAME:latest -f ../Dockerfile.alphapose ..
#docker tag $ALPHAPOSE_CONTAINER_NAME:latest $ALPHAPOSE_ECR
#docker push $ALPHAPOSE_ECR:latest

# Push and Build Animation image
#DOCKER_BUILDKIT=1 docker build -t $ANIMATION_CONTAINER_NAME:latest -f ../Dockerfile.animation-opencv ..
#docker tag $ANIMATION_CONTAINER_NAME:latest $ANIMATION_ECR
#docker push $ANIMATION_ECR:latest

# Push and Build Sketch Image 
#DOCKER_BUILDKIT=1 docker build -t $SKETCH_CONTAINER_NAME:latest -f ../Dockerfile.sketch_api ..
#docker tag $SKETCH_CONTAINER_NAME:latest $SKETCH_ECR
#docker push $SKETCH_ECR:latest
