
#curl -X POST http://localhost:5912/predictions/D2_humanoid_detector -T img/0004.png
# curl -d 'det_file_loc=/home/ap-server/torchserve_ap/scripts/sketch-DET.json' http://localhost:5912/predictions/alphapose

curl --silent --show-error --fail -o /dev/stderr -w "%{http_code}" -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'uuid=123' --data-urlencode image@gray_blur.png http://localhost:5912/predictions/alphapose 
[ $? -eq 200 ]