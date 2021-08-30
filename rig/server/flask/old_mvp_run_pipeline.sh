#!/bin/zsh


set -e
#set -x

echo start >> log.txt
date >> log.txt

UPLOAD_FN=${1}

INPUT_PARENT_DIR=/private/home/hjessmith/flask/input_parent_dir #/private/home/hjessmith/scripts/process_for_animation/${1}
INPUT_IMG_DIR=${INPUT_PARENT_DIR}/input/image

D2_OUTPUT_DIR=${INPUT_PARENT_DIR}/d2-out

rm -rf ${INPUT_PARENT_DIR}
mkdir -p ${INPUT_IMG_DIR}
cp uploads/${UPLOAD_FN} ${INPUT_IMG_DIR}



CURDIR=`pwd`

source ~/.bashrc

########### Run Detectron2 Humanoid Prediction ##########
conda activate detectron2-2

python /private/home/hjessmith/detectron2/detect-humanoids.py ${INPUT_IMG_DIR} ${D2_OUTPUT_DIR}

echo humanoid detect complete >> log.txt
date >> log.txt
########### Crop bounding boxes##########
python /private/home/hjessmith/scripts/04-19-2021/bbcrop_from_d2_pred.py ${INPUT_IMG_DIR} ${D2_OUTPUT_DIR} ${INPUT_PARENT_DIR}/cropped_detections/color ${INPUT_PARENT_DIR}/cropped_detections/gb
conda deactivate

# ########### Run Alphapose ##########
/private/home/hjessmith/scripts/04-19-2021/run_alphapose.sh ${INPUT_PARENT_DIR}/cropped_detections 
/private/home/hjessmith/scripts/04-19-2021/alphapose_visualize.sh ${INPUT_PARENT_DIR}/cropped_detections
echo pose detection complete >> log.txt
date >> log.txt

#./run_alphapose.sh ${INPUT_PARENT_DIR}/cropped
#./alphapose_visualize.sh ${INPUT_PARENT_DIR}/cropped

########### Segment ##########
mkdir -p ${INPUT_PARENT_DIR}/cropped_detections/mask
 
conda deactivate && conda activate detectron2

python /private/home/hjessmith/scripts/04-19-2021/skeleton_2_segmentation.py.bak ${INPUT_PARENT_DIR}/cropped_detections/alpha_pose_out/alphapose-results.json ${INPUT_PARENT_DIR}/cropped_detections/color ${INPUT_PARENT_DIR}/cropped_detections/mask

echo segmentation complete >> log.txt
date >> log.txt





########### Prep files for animation ##########

python old_mvp_prep_animation_files.py  ${UPLOAD_FN}

########### Animate ##########

conda deactivate && conda activate opengl

cd sketch_animate

# for running and jumping
DISPLAY=:100 ./main.sh config/render_${UPLOAD_FN%.*}.yaml cameras_ssf.yaml

/usr/bin/ffmpeg -y -r 30 -s 1500x800 -i sketch_animate/output/%04d.png -vcodec libx264 ../_out1.mp4
/usr/bin/ffmpeg -y -i ../_out1.mp4 -vf hflip -c:a copy ../_out2.mp4
ffmpeg -y -f concat -safe 0 -i /private/home/hjessmith/flask/_ffmpeg_concat_list.txt -c copy ../opengl_dev/out.mp4

echo ffmpeg complete >> log.txt
date >> log.txt
echo '******************' >> log.txt

# # for hip hop dance
# DISPLAY=:100 ./main.sh render_${UPLOAD_FN%.*}.yaml cameras_fff.yaml
# /usr/bin/ffmpeg -y -r 30 -s 1500x800 -i sketch_animate/output/%04d.png -vcodec libx264 ../out.mp4

# # # for wave hello
# DISPLAY=:100 ./main.sh render_${UPLOAD_FN%.*}.yaml cameras_fsf.yaml
# /usr/bin/ffmpeg -y -r 30 -s 1500x800 -i sketch_animate/output/%04d.png -vcodec libx264 ../out.mp4
