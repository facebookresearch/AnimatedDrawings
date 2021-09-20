
#curl -X POST http://localhost:5911/predictions/D2_humanoid_detector -T img/0004.png
curl -d 'det_file_loc=/home/model-server/torchserve_ap/sketch/sketch-DET.json' http://localhost:5911/predictions/alphapose