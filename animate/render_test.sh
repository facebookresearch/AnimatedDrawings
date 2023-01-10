

#MOTION_CONFIG=/home/headless_render/code/Data/motion_configs/hip_hop_dancing.yaml
#CHARACTER_CONFIG=/home/headless_render/code/Data/Texture/nick_cat.yaml
#OUTPUT_PATH=/home/headless_render/code

USER_CONFIG=./config/user_cfg_mesa_video_export.yaml
BVH_METADATA_CFG=./config/bvh_metadata_cfg.yml
CHAR_BVH_RETARGETING_CFG=./config/char_bvh_retargeting_cfg.yml
CHAR_METADATA_CFG=./tests/test_character/nick_cat.yaml

cd animator
python main.py ${USER_CONFIG} ${BVH_METADATA_CFG} ${CHAR_BVH_RETARGETING_CFG} ${CHAR_METADATA_CFG}