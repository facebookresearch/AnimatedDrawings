#!/bin/zsh

set -e
set -x
set -u


INPUT_DIR=${1}
OUTPUT_DIR=${2}

D2_PREDICTIONS_DIR=${OUTPUT_DIR}/d2_out
D2_PREDICTION_CROPPED_DIR=${OUTPUT_DIR}/cropped
D2_PREDICTION_CROPPED_GRAYBLUR_DIR=${OUTPUT_DIR}/cropped-gb

ALPHAPOSE_PREDICTIONS_DIR=${OUTPUT_DIR}/ap_out

source ~/.bashrc && conda activate ${D2_VIRTUAL_ENV_NAME}

python scripts/detect-humanoids.py ${INPUT_DIR} ${D2_PREDICTIONS_DIR} configs/humanoid_detection.yaml ${DETECTRON2_WEIGHTS_LOC}

python scripts/bbcrop_from_d2_pred.py ${INPUT_DIR} ${D2_PREDICTIONS_DIR} ${D2_PREDICTION_CROPPED_DIR} ${D2_PREDICTION_CROPPED_GRAYBLUR_DIR}

conda deactivate && conda activate ${AP_VIRTUAL_ENV_NAME}

CURDIR=`pwd`
cd ${ALPHAPOSE_PATH}
python scripts/demo_inference.py --cfg ${CURDIR}/configs/pose_detection.yaml \
				 --checkpoint ${ALPHAPOSE_WEIGHTS_LOC} \
				 --indir ${CURDIR}/${D2_PREDICTION_CROPPED_GRAYBLUR_DIR} \
				 --detfile ${CURDIR}/${OUTPUT_DIR}/sketch-DET.json
cd -
mv ${ALPHAPOSE_PATH}/examples/res ${ALPHAPOSE_PREDICTIONS_DIR}
if [ -d "${ALPHAPOSE_PATH}/examples/res" ]; then rm -Rf ${ALPHAPOSE_PATH}/examples/res; fi
if [ -d "${ALPHAPOSE_PATH}/examples" ]; then rm -Rf ${ALPHAPOSE_PATH}/examples; fi

AP_RESULTS_FN=${ALPHAPOSE_PREDICTIONS_DIR}/alphapose-results.json
AP_OUT_DIR=${ALPHAPOSE_PREDICTIONS_DIR}/imgs
CONFIDENCE_FN=${ALPHAPOSE_PREDICTIONS_DIR}/conf.csv
IMG_DIR=${D2_PREDICTION_CROPPED_DIR}	
python scripts/visualize_alphapose_predictions.py ${AP_RESULTS_FN} ${AP_OUT_DIR} ${CONFIDENCE_FN} ${IMG_DIR}

conda deactivate && conda activate ${D2_VIRTUAL_ENV_NAME}

MASK_OUTPUT=${OUTPUT_DIR}/mask
python scripts/skeleton_2_segmentation.py ${AP_RESULTS_FN} ${IMG_DIR} ${MASK_OUTPUT}

CHARACTER_OUT=${OUTPUT_DIR}/animation_files
python scripts/create_rigged_character_files.py ${MASK_OUTPUT} ${IMG_DIR} ${OUTPUT_DIR}/keypoints-postmask.json ${CHARACTER_OUT}
