

DOCKER_ID=`docker ps -a -q`

docker cp convert_ap_to_mar ${DOCKER_ID}:/home/convert_ap_to_mar
docker cp cropped_image.png ${DOCKER_ID}:/home/ap-server
docker cp eq.sh ${DOCKER_ID}:/home/ap-server
docker cp reg.sh ${DOCKER_ID}:/home/ap-server

