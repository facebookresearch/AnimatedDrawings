# Step 1. Main Docker setup

1. Update git submodules to update to out customized AlphaPose model.

```
git submodule init && git submodule update
```

2. Copy the model weights to the local root. see [rig/README.md](rig/README.md)

# Sketch Rig Build / Run

```shell
DOCKER_BUILDKIT=1 docker build -f Dockerfile.sketch_api --build-arg BUILD_CONFIG=development -t sketch_api .



docker run -p 5000:5000 --rm --env-file .env.aws-dev \
--mount type=bind,src="$(pwd)"/rig,dst=/home/model-server/rig \
--mount type=bind,src="$(pwd)"/tmp/uploads,dst=/home/model-server/rig/server/flask/uploads \
 -t sketch_api:latest
```

3. create your own .env environment. Copy from .env.default

4. Kick off a development build user docker-compose

```
docker-compose \
    -f docker-compose.development.yml \
    build \
    --build-arg USER_ID=$(id -u) \
    --build-arg GROUP_ID=$(id -g) \
```

5. Run the container

```
docker-compose \
-f docker-compose.development.yml \
up \
```

6. Single Build and run command (optional)

```
docker-compose \
    --env-file .env.profile \
    -f docker-compose.development.yml \
    build \
    --build-arg USER_ID=$(id -u) \
    --build-arg GROUP_ID=$(id -g)
&&
docker-compose     \
--env-file .env.profile  \
-f docker-compose.development.yml     \
up
```

# OLD Instructions [DEPRECATED]

3. Build the Docker Image using buildx

```
docker buildx build --file Dockerfile -t sketch:dev .
```

4. Create a network for the images to communicate

```
docker network create --driver bridge ap-net
```

4. Launch the docker Container

```
docker run -p 5000:5000 --name sketch_server --rm -a STDOUT \
-e REACT_APP_API_HOST=http://localhost:5000 \
--mount type=bind,src="$(pwd)"/videos,dst=/app/out/public/videos \
--network ap-net \
sketch:dev
```

where

| option                                               | effect                                                     |
| ---------------------------------------------------- | ---------------------------------------------------------- |
| -p 5000:5000                                         | maps port 5000 on the container to the host's port 5000    |
| --name                                               | instance name                                              |
| -rm                                                  | ??                                                         |
| -a STDOUT                                            | attach to stdout                                           |
| --mount type=bind,src=\<source\>,dst=\<destination\> | bind local "source" folder to the container "destination". |
| --network                                            | The network to join between images.                        |

OR to build and run in one step

```
docker buildx build --file Dockerfile -t sketch:dev . \
&& docker run -p 5000:5000 --name sketch_server --rm -a STDOUT \
-e REACT_APP_API_HOST=http://localhost:5000 \
--mount type=bind,src="$(pwd)"/videos,dst=/app/out/public/videos \
--network ap-net \
sketch:dev
```

# Step 2. Alpha Pose Docker Build.

## Build the Alpha Pose Torchserve image.

Note: This is run from the project root.

```
docker buildx build -f Dockerfile.alphapose -t alphapose:dev .
```

## Run the new image

```
docker run -a STDOUT -a STDERR --network ap-net --name alphapose_server --expose 5912 --rm alphapose:dev
```
