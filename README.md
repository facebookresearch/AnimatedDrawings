There are 5 key components that work together to create animations from image.

1. React UI [ui/www](ui/www)
2. API [rig/server/flask](rig/server/flask)
3. Detectron2 inference in Torchserve (for Image Segmentation and Masks) [torchserve_2](torchserve_d2)
4. AlphaPose inference in Torchserve (for Humanoid pose detection ) [torchserve_ap](torchserve_ap)
5. Animation code to generate animations video frames [animate](animate)

# Docker

Docker is used to build an image for each of the above component.

There are 3 flavors of docker build.

- development (for local development )
- profile (for profiling performance with functiontrace )
- release (for releasing on AWS )

# Local Development setup

## Step 1. Update git submodules to update to out customized AlphaPose model.

```
git submodule init && git submodule update
```

## 2. Copy the model archives to the local root.

see [rig/server/README.md](rig/server/README.md)

## 3. Create your own .env environment.

Copy from .env.default

```
cp .env.default .env
```

## 4. Kick off a development build user docker-compose

```shell
docker-compose -f docker-compose.development.yml build \
    --build-arg USER_ID=$(id -u) \
    --build-arg GROUP_ID=$(id -g)
```

## 5. Run the container

```
docker-compose -f docker-compose.development.yml up
```

## 6. Single Build and run command (optional)

```
docker-compose -f docker-compose.development.yml build \
    --build-arg USER_ID=$(id -u) \
    --build-arg GROUP_ID=$(id -g)
&& docker-compose -f docker-compose.development.yml up
```

# AWS Development setup

Developing on a AWS works the same as above only `DOCKER_BUILDKIT=1` must be used to use buildkit.

The necessary config changes are captured in [docker-compose.aws-dev.yml](docker-compose.aws-dev.yml) and [.env.aws-dev](.env.aws-dev)

```
DOCKER_BUILDKIT=1 docker-compose -f docker-compose.aws-dev.yml --env-file .env.aws-dev \
    build \
    --build-arg USER_ID=$(id -u) \
    --build-arg GROUP_ID=$(id -g)
&& docker-compose -f docker-compose.aws-dev.yml --env-file .env.aws-dev up
```

# Compiling Individual images

Individual images can be built and run independently. Please refer to the compose files for the necessary config settings.

## e.g. detectron

```shell
docker build -f Dockerfile.detectron_runtime -t detectron2:0.0.1 .

docker run --mount type=bind,source="$(pwd)/torchserve_d2/model_store",target=/home/model-server/model_store --rm -it -p 5911 detectron2:0.0.1
```

# Local Development setup

Steps for deploying to 'Staging'
