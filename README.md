# Docker setup

1. Update git submodules to update to out customized AlphaPose model.

`git submodule init && git submodule update`

2. Copy the model weights to the local root. see [rig/README.md](rig/README.md)

3. Build the Docker Image using buildx

`docker buildx build --file Dockerfile -t sketch:dev .`

4. Launch the docker Container

```
docker run -p 5000:5000 --name sketch_server --rm -a STDOUT \
-e REACT_APP_API_HOST=http://localhost:5000 \
--mount type=bind,src="$(pwd)"/videos,dst=/app/out/public/videos \
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

OR to build and run in one step

```
docker buildx build --file Dockerfile -t sketch:dev . \
&& docker run -p 5000:5000 --name sketch_server --rm -a STDOUT \
-e REACT_APP_API_HOST=http://localhost:5000 \
--mount type=bind,src="$(pwd)"/videos,dst=/app/out/public/videos \
sketch:dev
```
