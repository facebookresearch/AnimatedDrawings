# syntax = docker/dockerfile:1.2

ARG BUILD_IMAGE=continuumio/miniconda3
ARG PYTHON_VERSION=3.8

FROM ${BUILD_IMAGE} as build

ENV PYTHONUNBUFFERED TRUE
ENV CONDA_ALWAYS_COPY=true


RUN --mount=type=cache,target=/var/cache/apt,sharing=locked --mount=type=cache,target=/var/lib/apt \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
    ca-certificates \
    curl \
    zsh \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/* 

# ####################
# Detectron 2 - Build
###################### 
FROM build as detectron2_build

RUN --mount=type=cache,target=/opt/conda/pkgs \ 
    conda create --name detectron2 python=3.8.11

SHELL ["conda", "run", "-n", "detectron2", "/bin/bash", "-c"]

RUN  --mount=type=cache,target=/opt/conda/pkgs --mount=type=cache,target=/root/.cache/pip \
    conda install pytorch==1.9.0 torchvision==0.10.0 torchserve==0.4.0 cpuonly -c pytorch \
    && pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cpu/torch1.9/index.html \
    && conda install conda-pack \
    && pip install opencv-python==4.5.3.56

# Use conda-pack to create a standalone enviornment
# in /venv:
RUN conda-pack -n detectron2 -o /tmp/env.tar 
RUN mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
    rm /tmp/env.tar

# We've put venv in same path it'll be in final image,
# so now fix up paths:
RUN /venv/bin/conda-unpack



# ####################
# Detectron 2 - Runtime
###################### 
FROM ubuntu:18.04 AS detectron2_runtime

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
    ca-certificates \
    default-jre \
    && rm -rf /var/lib/apt/lists/* 

RUN useradd -m model-server 
USER model-server
WORKDIR /home/model-server

# Copy /venv from the previous stage:
COPY --from=detectron2_build /venv /venv


RUN mkdir -p /home/model-server/torchserve_d2
COPY --chown=model-server:model-server torchserve_d2/ /home/model-server/torchserve_d2

ENV PATH /venv/bin/:${PATH}

# start torchserve for detectron2 model in background
CMD ["/home/model-server/torchserve_d2/torchserve_start.sh"]


# ####################
# Sketch Rig - Build
# ####################
FROM build as rig_build

RUN --mount=type=cache,target=/opt/conda/pkgs conda create  --name flask python=3.7 -y
# Activate new shell with "flask" conda env
SHELL ["conda", "run", "-n", "flask", "/bin/bash", "-c"]
RUN --mount=type=cache,target=/opt/conda/pkgs --mount=type=cache,target=/root/.cache/pip \
    pip install flask flask_cors gunicorn imutils==0.5.4 opencv-python==4.5.3.56 \ 
    && conda install conda-pack scikit-image==0.18.1

# Use conda-pack to create a standalone enviornment
# in /venv:
RUN conda-pack -n flask -o /tmp/env.tar 
RUN mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
    rm /tmp/env.tar

# We've put venv in same path it'll be in final image,
# so now fix up paths:
RUN /venv/bin/conda-unpack




# ####################
# Flask Web App - Build
# ####################
FROM node:16.8.0 as build-deps-yarn
WORKDIR /usr/src/app
COPY ui/www/package.json ui/www/yarn.lock ./
RUN --mount=type=cache,target=/usr/src/app/.npm --mount=type=cache,target=/usr/src/app/node_modules \
    yarn
COPY ui/www ./
RUN --mount=type=cache,target=/usr/src/app/.npm --mount=type=cache,target=/usr/src/app/node_modules \
    yarn build


# ####################
# Sketch 2 - Runtime
###################### 
FROM ubuntu:18.04 AS rig_runtime

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked --mount=type=cache,target=/var/lib/apt,sharing=locked \
    # RUN \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
    ca-certificates \
    python3-opengl \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/* 

RUN useradd -m model-server 
USER model-server
WORKDIR /home/model-server

# Copy /venv from the previous stage:
COPY --from=rig_build /venv /venv

RUN mkdir -p /home/model-server/tmp \ 
    && mkdir -p /home/model-server/rig \
    && mkdir -p /home/model-server/rig/server \
    && mkdir -p /home/model-server/rig/server/in \
    && mkdir -p /home/model-server/rig/server/out 

ENV TEMP=/home/model-server/tmp
ENV PATH /venv/bin/:${PATH}

COPY --chown=model-server:model-server rig rig/

WORKDIR /home/model-server/rig/server/flask 
RUN mkdir uploads && mkdir output_predictions && mkdir consent_given_upload_copies

EXPOSE 5000


# ####################
# Flask Web App  
###################### 
WORKDIR /home/model-server/rig/server/flask 
COPY --chown=model-server:model-server ui/www/.env .
COPY --chown=model-server:model-server ui/www/env.sh .
RUN chmod +x env.sh
COPY --from=build-deps-yarn --chown=model-server:model-server /usr/src/app/build /home/model-server/rig/server/flask/static


# Define the default command.
CMD [ "./run.sh" ]

# CMD [ "sleep", "infinity" ]

