# syntax = docker/dockerfile:1.2

# --platform=linux/amd64  necessary on M1 Apple Silicon Mac: https://stackoverflow.com/questions/71040681/qemu-x86-64-could-not-open-lib64-ld-linux-x86-64-so-2-no-such-file-or-direc
FROM --platform=linux/amd64 ubuntu:18.04

ENV PYTHONUNBUFFERED TRUE

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked --mount=type=cache,target=/var/lib/apt \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
    ca-certificates \
    wget \
    libtbb2 \
    python3-opengl \
    libglfw3 \ 
    libglfw3-dev \
    libglew2.0 \
    libgl1-mesa-glx \
    libosmesa6 \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m headless_render 
WORKDIR /home/headless_render
USER headless_render

RUN mkdir -p ~/miniconda3 \
&& wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh \
&& bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3 \
&& rm -rf ~/miniconda3/miniconda.sh \
&& ~/miniconda3/bin/conda init bash \
&& ~/miniconda3/bin/conda init zsh 

RUN mkdir -p /home/headless_render/code
COPY animate/requirements.txt .
COPY animate/conda-env.txt .

ENTRYPOINT ["tail", "-f", "/dev/null"]