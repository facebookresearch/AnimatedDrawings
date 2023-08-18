# Generate Avatar Animations

This is a fork of Facebook's [Animated Drawings](https://github.com/facebookresearch/AnimatedDrawings). For installation instructions and project usage, please take a look at their [README.md](https://github.com/facebookresearch/AnimatedDrawings/blob/main/examples/config/README.md). This project is meant to be utilized alongside [Interactive Talking Avatar](https://github.com/AmberLien/interactive-talking-avatar) in its development phase to generate body and talking animations for your custom avatar.

### Generating Body Animations

In order to generate the animations for your character, we need to generate annotation files. Rather than do so manually, Facebook has trained a drawn humanoid figure detector and post estimator to generate the annotation files using the model predictions.

To use the model, you must set up a Docker container that runs TorchServe.

To set up the container,

1. [Install Docker Desktop](https://docs.docker.com/get-docker/)
2. Ensure Docker Desktop is running.
3. Run the following commands, starting from the Animated Drawings root directory:

````bash
    (animated_drawings) AnimatedDrawings % cd torchserve

    # build the docker image... this takes a while (~5-7 minutes on Macbook Pro 2021)
    (animated_drawings) torchserve % docker build -t docker_torchserve .

    # start the docker container and expose the necessary ports
    (animated_drawings) torchserve % docker run -d --name docker_torchserve -p 8080:8080 -p 8081:8081 docker_torchserve
````

Wait ~10 seconds, then ensure Docker and TorchServe are working by pinging the server:

````bash
    (animated_drawings) torchserve % curl http://localhost:8080/ping

    # should return:
    # {
    #   "status": "Healthy"
    # }
````

If, after waiting, the response is `curl: (52) Empty reply from server`, one of two things is likely happening.
1. Torchserve hasn't finished initializing yet, so wait another 10 seconds and try again.
2. Torchserve is failing because it doesn't have enough RAM.  Try [increasing the amount of memory available to your Docker containers](https://docs.docker.com/desktop/settings/mac/#advanced) to 16GB by modifying Docker Desktop's settings.

Now you can generate body animations for your character by doing the following:

````bash
    (animated_drawings) torchserve % cd ../examples
    (animated_drawings) examples % python talking_avatar.py "https://preview.bitmoji.com/avatar-builder-v3/preview/body?scale=3&gender=1&style=1&rotation=0&outfit=" talking_avatar_out
````

An image of the avatar you previously customized is generated and then analyzed to create multiple animations using BVH motion data from a human actor. The resulting animations will be saved in './custom_animations'. Each avatar you create will have its own image and folder containing that avatar's animations named as your input or, if not provided, a randomly generated id.

<!--

### Generating Talking Animation

To generate talking animations, navigate to the root directory of the project. Then navigate to examples and run the following command.

````bash
    (animated_drawings) examples % python generate_talking_animation.py "https://preview.bitmoji.com/avatar-builder-v3/preview/body?scale=3&gender=1&style=1&rotation=0&outfit=" talking_animation_out
````

An image of the avatar you customized is generated using the url. Then, various mouth shapes are overlayed and combined to form a gif that is the character's talking animation. The resulting gif was saved as './talking_animation_out.gif'
-->
