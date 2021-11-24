# Step 1. Main Docker setup

1. Update git submodules to update to out customized AlphaPose model.

```
git submodule init && git submodule update
```

2. Copy the model weights to the local root. see [rig/README.md](rig/README.md)

3. create your own .env environment. Copy from .env.default

4. Create an Open CV Build
``` shell
docker build -f Dockerfile.opencv -t opencv:4.3.0 .
```

5. Kick off a development build user docker-compose

``` shell
docker-compose \
    -f docker-compose.development.yml \
    build \
    --build-arg USER_ID=$(id -u) \
    --build-arg GROUP_ID=$(id -g) 
```

6. Run the container

```
docker-compose \
-f docker-compose.development.yml \
up 
```

7. Single Build and run command (optional)

```
docker-compose \
    -f docker-compose.development.yml \
    build \
    --build-arg USER_ID=$(id -u) \
    --build-arg GROUP_ID=$(id -g)
&&
docker-compose     \
-f docker-compose.development.yml     \
up
```

