
MODEL_NAME=alphapose
SERIALIZED_FILE=$PWD/weights/alphapose_weights.jit
VERSION=1.0
YAML_FILE=$PWD/configs/pose_detection.yaml
HANDLER=$PWD/handler.py

torch-model-archiver --model-name ${MODEL_NAME} --version ${VERSION} --serialized-file ${SERIALIZED_FILE} --extra-files ${YAML_FILE} --handler ${HANDLER}

mv *.mar ../torchserve_ap/model_store