
MODEL_NAME=alphapose
SERIALIZED_FILE=/home/model-server/convert_to_mar/alphapose_weights.ts
VERSION=1.0
YAML_FILE=/home/model-server/convert_to_mar/pose_detection.yaml
HANDLER=/home/model-server/convert_to_mar/handler.py

torch-model-archiver --model-name ${MODEL_NAME} --version ${VERSION} --serialized-file ${SERIALIZED_FILE} --extra-files ${YAML_FILE} --handler ${HANDLER}

mv *.mar model_store