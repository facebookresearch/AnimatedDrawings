#!/bin/bash

# Set ACCOUNT_ID and REGION variables 
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=$(curl -s http://169.254.169.254/latest/dynamic/instance-identity/document|jq -r .region)



# Set ANIMATION_ECR and ANIMATION_CONTAINER_NAME
ANIMATION_ECR=$(terraform output --json  | jq -r .animation_ecr.value)
ANIMATION_CONTAINER_NAME=$(terraform output --json | jq -r .animation_container_name.value)




### LOG IN TO ECR.
### BUILD, TAG AND PUSH RESPECTIVE IMAGES


# Authenticate into ECR
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.us-east-2.amazonaws.com

# Push and Build Animation image
DOCKER_BUILDKIT=1 docker build -t $ANIMATION_CONTAINER_NAME:latest -f ../Dockerfile.animation-opencv ..
docker tag $ANIMATION_CONTAINER_NAME:latest $ANIMATION_ECR
docker push $ANIMATION_ECR:latest

