# syntax = docker/dockerfile:1.2

FROM continuumio/miniconda3

# install os dependencies
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

# install python dependencies
RUN pip install openmim
RUN pip install torch
RUN mim install mmcv-full==1.7.0
RUN pip install mmpose==0.29.0
RUN pip install mmdet==2.27.0
RUN pip install torchserve

# prep torchserve
RUN mkdir -p /home/torchserve/model-store
RUN wget https://github.com/facebookresearch/AnimatedDrawings/releases/download/v0.0.1/drawn_humanoid_detector.mar -P /home/torchserve/model-store/
RUN wget https://github.com/facebookresearch/AnimatedDrawings/releases/download/v0.0.1/drawn_humanoid_pose_estimator.mar -P /home/torchserve/model-store/
COPY config.properties /home/torchserve/config.properties

# starting command
CMD /opt/conda/bin/torchserve --start --ts-config /home/torchserve/config.properties && sleep infinity
