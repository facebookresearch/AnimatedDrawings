#!/bin/zsh

set -e
set -x

UUID=${1}
ANIMATION_TYPE=${2}
VIDEO_SHARE_ROOT=${3}
OUTPUT_PARENT_DIR=/home/model-server/rig/server/flask/output_predictions/${UUID}
CHARACTER_CONFIG=${OUTPUT_PARENT_DIR}/animation/cropped_image.yaml
VIDEO_SHARE_DIR=${VIDEO_SHARE_ROOT}/${UUID}

source ~/.bashrc

# ########### Animate ##########
# prep image output space
rm -rf ${OUTPUT_PARENT_DIR}/animation/output_images
mkdir ${OUTPUT_PARENT_DIR}/animation/output_images

#conda activate opengl
 

if [ "$ANIMATION_TYPE" = "run_jump" ]; then
	MOTION_CONFIG=/home/model-server/animate/Data/motion_configs/running_jump.yaml
	MIRROR_CONCAT=1
elif [ "$ANIMATION_TYPE" = "dance" ]; then
	MOTION_CONFIG=/home/model-server/animate/Data/motion_configs/hip_hop_dancing.yaml
	MIRROR_CONCAT=0
elif [ "$ANIMATION_TYPE" = "wave" ]; then
	MOTION_CONFIG=/home/model-server/animate/Data/motion_configs/wave_hello_3.yaml
	MIRROR_CONCAT=0
fi

cd ~/animate/sketch_animate

rm -rf ${OUTPUT_PARENT_DIR}/animation/output_images
mkdir -p ${OUTPUT_PARENT_DIR}/animation/output_images

conda run -v -n sketch_animate python main.py ${MOTION_CONFIG} ${CHARACTER_CONFIG} ${OUTPUT_PARENT_DIR}/animation/output_images

if [ ${MIRROR_CONCAT} -eq 1 ]; then
	/usr/bin/ffmpeg -y -r 18 -s 1920x1080 -i ${OUTPUT_PARENT_DIR}/animation/output_images/%04d.png -vcodec libx264 -pix_fmt yuv420p ${OUTPUT_PARENT_DIR}/animation/_out1.mp4
	/usr/bin/ffmpeg -y -i ${OUTPUT_PARENT_DIR}/animation/_out1.mp4 -vf hflip -c:a copy ${OUTPUT_PARENT_DIR}/animation/_out2.mp4
	ffmpeg -y -f concat -safe 0 -i <(printf "file '${OUTPUT_PARENT_DIR}/animation/_out1.mp4'\nfile '${OUTPUT_PARENT_DIR}/animation/_out2.mp4'\n") -c copy ${OUTPUT_PARENT_DIR}/animation/${ANIMATION_TYPE}.mp4
	rm -rf ${OUTPUT_PARENT_DIR}/animation/_out1.mp4
	rm -rf ${OUTPUT_PARENT_DIR}/animation/_out2.mp4
else
	/usr/bin/ffmpeg -y -r 18 -s 1500x800 -i ${OUTPUT_PARENT_DIR}/animation/output_images/%04d.png -vcodec libx264 -pix_fmt yuv420p ${OUTPUT_PARENT_DIR}/animation/${ANIMATION_TYPE}.mp4
fi
# Copy files to output dir
mkdir -p ${VIDEO_SHARE_DIR}
cp ${OUTPUT_PARENT_DIR}/animation/${ANIMATION_TYPE}.mp4 ${VIDEO_SHARE_DIR}/${ANIMATION_TYPE}.mp4
