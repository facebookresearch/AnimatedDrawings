# syntax = docker/dockerfile:1.2

FROM continuumio/miniconda3

# install os dependencies
RUN mkdir -p /usr/share/man/man1
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

WORKDIR "/python"

# conda
SHELL ["/bin/bash", "--login", "-c"]
RUN conda create --name animated_drawings python=3.8.13
RUN conda init bash
RUN conda activate animated_drawings

# install python dependencies
COPY . .
RUN pip install -e .

# starting command
ENTRYPOINT ["python examples/handler.py"]
