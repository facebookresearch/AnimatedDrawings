#!/bin/bash

#ecs-cli configure --cluster ML_DEVOPS_CLUSTER_QA --default-launch-type FARGATE --config-name MLDEVOPS-Cluster-Config --region us-east-2
ecs-cli compose --cluster-config MLDEVOPS-Cluster-Config --project-name MLDEVOPS_SERVICE service up --create-log-groups \
--target-group-arn arn:aws:elasticloadbalancing:us-east-2:790537050551:targetgroup/ml-devops-tg-QA/868fb22cf427bf4c --container-name detectron2_model --container-port 5911
