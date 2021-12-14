This directory contains the files necessary to generate alphapose.mar file on the Docker.

First make sure weights are within the weights folder.

next run ./a_weights_to_ts/convert_to_torchscript.sh

next run ./b_ts_to_mar/torch-model-archiver.sh

