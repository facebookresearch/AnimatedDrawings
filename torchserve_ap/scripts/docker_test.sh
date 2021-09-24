

cd /home/ap-server/torchserve_ap

torchserve --start --model-store model_store --models alphapose.mar --ts-config config.properties


cd /home/ap-server/torchserve_ap/scripts
sleep 3 # wait for torchserve to spin up. 

./example_query.sh

torchserve --stop