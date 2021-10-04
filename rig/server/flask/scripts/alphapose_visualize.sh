#!/bin/bash

set -e
set -x
set -u

PARENT_INDIR=${1}  

RESULTS_FN=${PARENT_INDIR}/alphapose_results.json
OUT_DIR=${PARENT_INDIR}
CONFIDENCE_FN=${PARENT_INDIR}/joint_confidence.csv

IMG_DIR=${PARENT_INDIR}
 
conda run -v -n alphapose python scripts/visualize_alphapose_predictions.py ${RESULTS_FN} ${OUT_DIR} ${CONFIDENCE_FN} ${IMG_DIR}

