# syntax = docker/dockerfile:1.2

ARG BASE_IMAGE=ubuntu:18.04
ARG PYTHON_VERSION=3.8

FROM ${BASE_IMAGE} as dev-base

ENV PYTHONUNBUFFERED TRUE

# --mount=type=cache,id=apt-dev,target=/var/cache/apt \

RUN --mount=type=cache,target=/var/cache/apt --mount=type=cache,target=/var/lib/apt \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
    ca-certificates \
    curl \
    python3 \
    python3-dev \
    git \ 
    zsh \
    gcc \ 
    g++ \
    python3-opengl \
    libglfw3 \ 
    libglfw3-dev \
    libglew2.0 \
    libgl1-mesa-glx \
    libosmesa6 \
    libglib2.0-0 \
    ffmpeg \
    openjdk-11-jdk \
    && rm -rf /var/lib/apt/lists/* 
RUN cd /tmp \
    && curl -O https://bootstrap.pypa.io/get-pip.py \
    && python3 get-pip.py

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1
RUN update-alternatives --install /usr/local/bin/pip pip /usr/local/bin/pip3 1


# Add Conda to path:
ENV PATH /home/model-server/conda/bin:$PATH
ENV PATH /home/model-server/conda/envs/env/bin:$PATH

FROM dev-base as conda
RUN useradd -m model-server 
USER model-server
WORKDIR /home/model-server

RUN --mount=type=cache,target=/opt/conda/pkgs \
    curl -fsSL -v -o ~/miniconda.sh -O  https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh  && \
    chmod +x ~/miniconda.sh && \
    ~/miniconda.sh -b -p /home/model-server/conda && \
    rm ~/miniconda.sh && \
    /home/model-server/conda/bin/conda install -y python=${PYTHON_VERSION} conda-build pyyaml numpy ipython&& \
    /home/model-server/conda/bin/conda clean -ya



FROM conda as sketch_animate

RUN mkdir -p /home/model-server/tmp \ 
    && mkdir -p /home/model-server/rig \
    && mkdir -p /home/model-server/rig/server \
    && mkdir -p /home/model-server/rig/server/in \
    && mkdir -p /home/model-server/rig/server/out \
    && mkdir -p /home/model-server/animate \
    && mkdir -p /home/model-server/animate/output \
    && mkdir -p /home/model-server/animate/sketch_animate/output 


COPY --chown=model-server:model-server animate/conda-env.txt animate/conda-env.txt
COPY --chown=model-server:model-server animate/requirements.txt animate/requirements.txt
WORKDIR /home/model-server/animate
RUN --mount=type=cache,target=/opt/conda/pkgs \
    conda create --name sketch_animate --file conda-env.txt
SHELL ["conda","run","-n","sketch_animate","/bin/bash","-c"]

RUN --mount=type=cache,target=/opt/conda/pkgs \ 
    --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

WORKDIR /home/model-server
COPY --chown=model-server:model-server animate animate/


# "glfw", "egl", or "osmesa" from https://github.com/deepmind/dm_control#rendering
ENV MUJOCO_GL="osmesa"

ENV TEMP=/home/model-server/tmp

#  TODO Clean up

FROM sketch_animate as sketch_rig


ENV DETECTRON2_WEIGHTS_LOC=/home/model-server/detectron2_weights.pth
ENV ALPHAPOSE_WEIGHTS_LOC=/home/model-server/alphapose_weights.pth
ENV D2_VIRTUAL_ENV_NAME=detectron2
ENV AP_VIRTUAL_ENV_NAME=alphapose

RUN --mount=type=cache,target=/opt/conda/pkgs \ 
    conda create --name detectron2 python=3.8.11

# && python -m pip install 'git+https://github.com/facebookresearch/detectron2.git' \

SHELL ["conda", "run", "-n", "detectron2", "/bin/bash", "-c"]

RUN  --mount=type=cache,target=/opt/conda/pkgs --mount=type=cache,target=/root/.cache/pip \
    conda install pytorch==1.9.0 torchvision==0.10.0 cpuonly -c pytorch \
    && pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cpu/torch1.9/index.html \
    && conda install torchserve==0.4.0 -c pytorch \
    && pip install opencv-python==4.5.3.56
# conda install opencv==4.5.3 -c conda-forge \
# && conda install scikit-image \
# && conda install scikit-learn \ 
# && conda install natsort \

RUN mkdir -p /home/model-server/torchserve_d2
COPY --chown=model-server:model-server torchserve_d2/ /home/model-server/torchserve_d2

# sketch_rig
RUN conda create  --name alphapose python=3.6 -y
# Activate new shell with conda env
SHELL ["conda", "run", "-n", "alphapose", "/bin/bash", "-c"]

# The following is from here: https://github.com/MVIG-SJTU/AlphaPose/blob/master/docs/INSTALL.md \
RUN --mount=type=cache,target=/opt/conda/pkgs --mount=type=cache,target=/root/.cache/pip \
    conda install pytorch-cpu==1.1.0 torchvision-cpu==0.3.0 cpuonly -c pytorch \
    # && git clone https://github.com/MVIG-SJTU/AlphaPose.git \
    && export PATH=/usr/local/cuda/bin/:$PATH \
    && export LD_LIBRARY_PATH=/usr/local/cuda/lib64/:$LD_LIBRARY_PATH \
    && pip install cython pycocotools \
    && conda install matplotlib 
# && conda install -c conda-forge  pycocotools\
ENV CUDA_HOME=/usr/local/cuda
ENV ALPHAPOSE_PATH=/home/model-server/AlphaPose
COPY --chown=model-server:model-server AlphaPose AlphaPose/

# Compile alphapose
RUN  --mount=type=cache,target=/opt/conda/pkgs --mount=type=cache,target=/root/.cache/pip \
    cd AlphaPose \
    && python3 setup.py build develop --user 


# RUN cp /home/model-server/rig/server/input/0004.png /home/model-server/rig/server/in 

SHELL ["/bin/bash","-c"]
RUN conda init

FROM sketch_rig as sketch_flask

RUN conda create  --name flask python=3.7 -y
# Activate new shell with "flask" conda env
SHELL ["conda", "run", "-n", "flask", "/bin/bash", "-c"]
RUN --mount=type=cache,target=/opt/conda/pkgs --mount=type=cache,target=/root/.cache/pip \
    pip install flask flask_cors gunicorn opencv-python==4.5.3.56 imutils==0.5.4 \
    && conda install scikit-image==0.18.1

RUN mkdir -p /home/model-server/models/model_store
COPY --chown=model-server:model-server torchserve_d2/model_store  /home/model-server/models/model_store
COPY --chown=model-server:model-server  alphapose_weights.pth /home/model-server/models

COPY --chown=model-server:model-server rig rig/

WORKDIR /home/model-server/rig/server/flask 
RUN mkdir uploads && mkdir output_predictions

EXPOSE 5000

# Build the Web App

FROM node:16.8.0 as build-deps-yarn
WORKDIR /usr/src/app
COPY ui/www/package.json ui/www/yarn.lock ./
RUN --mount=type=cache,target=/usr/src/app/.npm --mount=type=cache,target=/usr/src/app/node_modules \
    yarn
COPY ui/www ./
RUN --mount=type=cache,target=/usr/src/app/.npm --mount=type=cache,target=/usr/src/app/node_modules \
    yarn build


# Copy the webapp

FROM sketch_flask
COPY --chown=model-server:model-server ui/www/.env .
COPY --chown=model-server:model-server ui/www/env.sh .
RUN chmod +x env.sh
COPY --from=build-deps-yarn --chown=model-server:model-server /usr/src/app/build /home/model-server/rig/server/flask/static


# Define the default command.
CMD [ "./run.sh" ]

# CMD [ "sleep", "infinity" ]

