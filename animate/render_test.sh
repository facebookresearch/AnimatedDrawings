

MOTION_CONFIG=/home/headless_render/code/Data/motion_configs/hip_hop_dancing.yaml
CHARACTER_CONFIG=/home/headless_render/code/Data/Texture/nick_cat.yaml

OUTPUT_PATH=/home/headless_render/code

cd animator
python main.py ${MOTION_CONFIG} ${CHARACTER_CONFIG} ${OUTPUT_PATH}