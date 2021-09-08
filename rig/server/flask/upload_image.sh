#!/bin/zsh

set -e
set -x

UPLOAD_FN=${1}
UUID=${2}

OUTPUT_PARENT_DIR='output_predictions/'${UUID}
mkdir -p ${OUTPUT_PARENT_DIR}
mv uploads/${UPLOAD_FN} ${OUTPUT_PARENT_DIR}/image.png
