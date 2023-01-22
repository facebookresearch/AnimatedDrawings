#!/bin/bash
# Copyright (c) Meta Platforms, Inc. and affiliates.

# stop if already running
echo Stopping TorchServe...
torchserve --stop

# start torchserve with config.properties, log output
echo Starting TorchServe...
mkdir -p ./logs
torchserve --start --ts-config config.properties >> ./logs/torch_server.log 2>&1 &
