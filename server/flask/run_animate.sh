#!/bin/zsh

set -e
set -x

UUID=${1}
ANIMATION_TYPE=${2}
OUTPUT_PARENT_DIR='/private/home/hjessmith/flask/output_predictions/'${UUID}

source ~/.bashrc

# ########### Animate ##########
# prep image output space
rm -rf ${OUTPUT_PARENT_DIR}/animation/output_images
mkdir ${OUTPUT_PARENT_DIR}/animation/output_images

conda activate opengl
 
cd sketch_animate

if [ "$ANIMATION_TYPE" = "run_jump" ]; then
	DISPLAY=:100 ./main.sh ${OUTPUT_PARENT_DIR}/animation/render_run_jump.yaml cameras_ssf.yaml
	/usr/bin/ffmpeg -y -r 30 -s 1500x800 -i ${OUTPUT_PARENT_DIR}/animation/output_images/%04d.png -vcodec libx264 -pix_fmt yuv420p ${OUTPUT_PARENT_DIR}/animation/_out1.mp4
	/usr/bin/ffmpeg -y -i ${OUTPUT_PARENT_DIR}/animation/_out1.mp4 -vf hflip -c:a copy ${OUTPUT_PARENT_DIR}/animation/_out2.mp4
	ffmpeg -y -f concat -safe 0 -i <(printf "file '${OUTPUT_PARENT_DIR}/animation/_out1.mp4'\nfile '${OUTPUT_PARENT_DIR}/animation/_out2.mp4'\n") -c copy ${OUTPUT_PARENT_DIR}/animation/${ANIMATION_TYPE}.mp4
	rm -rf ${OUTPUT_PARENT_DIR}/animation/_out1.mp4
	rm -rf ${OUTPUT_PARENT_DIR}/animation/_out2.mp4

elif [ "$ANIMATION_TYPE" = "dance" ]; then
	DISPLAY=:100 ./main.sh ${OUTPUT_PARENT_DIR}/animation/render_dance.yaml cameras_fff.yaml
	/usr/bin/ffmpeg -y -r 30 -s 1500x800 -i ${OUTPUT_PARENT_DIR}/animation/output_images/%04d.png -vcodec libx264 -pix_fmt yuv420p ${OUTPUT_PARENT_DIR}/animation/${ANIMATION_TYPE}.mp4

elif [ "$ANIMATION_TYPE" = "wave" ]; then
	DISPLAY=:100 ./main.sh ${OUTPUT_PARENT_DIR}/animation/render_wave.yaml cameras_fsf.yaml
	/usr/bin/ffmpeg -y -r 30 -s 1500x800 -i ${OUTPUT_PARENT_DIR}/animation/output_images/%04d.png -vcodec libx264 -pix_fmt yuv420p ${OUTPUT_PARENT_DIR}/animation/${ANIMATION_TYPE}.mp4
fi

conda deactivate
