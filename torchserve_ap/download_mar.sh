#!/bin/bash


## Make Authenticated API Call to S3 Bucket to download mar file
aws s3 cp s3://prod-demo-sketch-in-model-store/alphapose.mar /home/ap-server/torchserve_ap/.
