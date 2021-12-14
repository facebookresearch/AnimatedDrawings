
pip install torch-model-archiver
cd /home/convert_ap_to_mar/b_ts_to_mar
./torch-model-archiver.sh
mv alphapose.mar /home/ap-server/model_store
torchserve --stop

