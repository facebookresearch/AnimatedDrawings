#!/bin/bash

## Create Model Store Directory
echo "Downloading Model Store in: $(pwd)"

## Make Authenticated API Call to S3 Bucket to download mar file
aws s3 cp s3://dev-demo-sketch-in-model-store/D2_humanoid_detector.mar /home/model-server/torchserve_d2/.
