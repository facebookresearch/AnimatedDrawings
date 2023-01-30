# syntax = docker/dockerfile:1.2

FROM continuumio/miniconda3
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
    ca-certificates \
    curl \
    python3-pip \
    vim \
    sudo \
    default-jre \
    git \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install openmim
RUN pip install torch
RUN mim install mmcv-full==1.7.0
RUN pip install mmpose==0.29.0
RUN pip install mmdet==2.27.0
RUN pip install torchserve

CMD /opt/conda/bin/torchserve --start --ts-config /home/torchserve/config.properties && sleep infinity