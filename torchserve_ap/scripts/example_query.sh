
#curl -X POST http://localhost:5912/predictions/D2_humanoid_detector -T img/0004.png
curl -d 'det_file_loc=/home/ap-server/torchserve_ap/scripts/sketch-DET.json' http://localhost:5912/predictions/alphapose