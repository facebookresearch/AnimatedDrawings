# Docker setup

1. Update git submodules to update to out customized AlphaPose model.

`git submodule init && git submodule update`

2. Copy the model weights to the local root. see [rig/README.md](rig/README.md)

3. Build the Docker Image

`docker build --file Dockerfile -t sketch:dev .`

4. Launch the docker Container

```
docker run -p 5000:5000 --name sketch_server --rm -a STDOUT \
-e REACT_APP_API_HOST=http://localhost:5000 \
sketch:dev
```

OR to build and run in one step

```
docker build --file Dockerfile -t sketch:dev . \
&& docker run -p 5000:5000 --name sketch_server --rm -a STDOUT \
-e REACT_APP_API_HOST=http://localhost:5000 \
sketch:dev
```
