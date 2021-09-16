#!/bin/zsh

set -e
set -x

WORK_DIR=${1}
ANIMATION_TYPE=${2}
VIDEO_SHARE_DIR=${3}

CHARACTER_CONFIG=${WORK_DIR}/animation/cropped_image.yaml

source ~/.bashrc

# ########### Animate ##########
# prep image output space
rm -rf ${WORK_DIR}/animation/output_images
mkdir ${WORK_DIR}/animation/output_images

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

rm -rf ${WORK_DIR}/animation/output_images
mkdir -p ${WORK_DIR}/animation/output_images

conda run -v -n sketch_animate python main.py ${MOTION_CONFIG} ${CHARACTER_CONFIG} ${WORK_DIR}/animation/output_images

if [ ${MIRROR_CONCAT} -eq 1 ]; then
	/usr/bin/ffmpeg -y -r 18 -s 1920x1080 -i ${WORK_DIR}/animation/output_images/%04d.png -vcodec libx264 -pix_fmt yuv420p ${WORK_DIR}/animation/_out1.mp4
	/usr/bin/ffmpeg -y -i ${WORK_DIR}/animation/_out1.mp4 -vf hflip -c:a copy ${WORK_DIR}/animation/_out2.mp4
	ffmpeg -y -f concat -safe 0 -i <(printf "file '${WORK_DIR}/animation/_out1.mp4'\nfile '${WORK_DIR}/animation/_out2.mp4'\n") -c copy ${WORK_DIR}/animation/${ANIMATION_TYPE}.mp4
	rm -rf ${WORK_DIR}/animation/_out1.mp4
	rm -rf ${WORK_DIR}/animation/_out2.mp4
else
	/usr/bin/ffmpeg -y -r 18 -s 1500x800 -i ${WORK_DIR}/animation/output_images/%04d.png -vcodec libx264 -pix_fmt yuv420p ${WORK_DIR}/animation/${ANIMATION_TYPE}.mp4
fi

# Copy files to output dir
mkdir -p ${VIDEO_SHARE_DIR}
mv ${WORK_DIR}/animation/${ANIMATION_TYPE}.mp4 ${VIDEO_SHARE_DIR}/${ANIMATION_TYPE}.mp4

# Clean up
rm ${WORK_DIR}/animation/output_images/*.png
