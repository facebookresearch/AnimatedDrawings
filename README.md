# Step 1. Main Docker setup

1. Update git submodules to update to out customized AlphaPose model.

```
git submodule init && git submodule update
```

2. Copy the model weights to the local root. see [rig/README.md](rig/README.md)

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
