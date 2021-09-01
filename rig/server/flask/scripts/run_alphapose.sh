#!/bin/zsh

set -e
set -x
set -u

PARENT_INDIR=${1}  

#DETFILE=${PARENT_INDIR}/sketch-DET.json
#OUTDIR=${PARENT_INDIR}/alpha_pose_out

# BATCH_NAME=04-23-real
# EPOCH_NUMBER=299
# CONFIG=/private/home/hjessmith/Synthetic2DCharacterGeneration/syntheticclusters/${BATCH_NAME}/alpha_pose/${BATCH_NAME}.yaml
# CHECKPOINT=/private/home/hjessmith/Synthetic2DCharacterGeneration/syntheticclusters/${BATCH_NAME}/alpha_pose/trained_weights/model_${EPOCH_NUMBER}.pth


CONFIG=/private/home/hjessmith/05-07-21-bicyclegantest/condition4/05-07-21-bgtest-condition4.yaml 
CHECKPOINT=/private/home/hjessmith/05-07-21-bicyclegantest/condition4/exp_05-07-21-bgtest-condition4-05-07-21-bgtest-condition4.yaml/model_299.pth
#CHECKPOINT=/private/home/hjessmith/scratch/alphapose_weights.pth

# BATCH_NAME=tadpole
# EPOCH_NUMBER=89
# CONFIG=/private/home/hjessmith/Synthetic2DCharacterGeneration/syntheticclusters/${BATCH_NAME}/c0/alpha_pose/${BATCH_NAME}_c0.yaml
# CHECKPOINT=/private/home/hjessmith/Synthetic2DCharacterGeneration/syntheticclusters/${BATCH_NAME}/c0/alpha_pose/trained_weights/model_${EPOCH_NUMBER}.pth

source ~/.bashrc && conda activate alphapose

cd /private/home/hjessmith/alphapose/AlphaPose

python scripts/demo_inference.py --cfg ${CONFIG} --checkpoint ${CHECKPOINT} --indir ${PARENT_INDIR} --detfile ${PARENT_INDIR}/sketch-DET.json
                                        
#if [[ ! -e $OUTDIR ]]; then
#    mkdir $OUTDIR
#fi

mv examples/res/alphapose-results.json ${PARENT_INDIR}/alphapose_results.json
