#!/bin/bash


MODEL_NAME=D2_humanoid_detector
SERIALIZED_FILE=weights/model.ts
VERSION=1.0
YAML_FILE=configs/d2_config.yaml
HANDLER=d2_handler.py

torch-model-archiver --model-name ${MODEL_NAME} --version ${VERSION} --serialized-file ${SERIALIZED_FILE} --extra-files ${YAML_FILE} --handler ${HANDLER}

mv *.mar model_store
