# Animated Drawings
This is a repo to prepare the open-source release of the Animated Drawings code.

If you are looking for the code behind sketch.metademolab.com, see [https://github.com/fairinternal/sketch_rig](https://github.com/fairinternal/sketch_rig)



From local computer:

    # create env if needed
    cd ${PROJECTROOT}/animate
    conda env create --name sketch_animate --file=conda-env-dev.yaml
    conda activate sketch_test
    pip install -e .
    
    cd animator
    python main_dev.py
    
You may also need to install the glfw libraries [via brew](https://formulae.brew.sh/formula/glfw)
    
If everything is working correctly, you should see a black box in the middle of a light purple void

<img width="503" alt="Screen Shot 2022-12-05 at 5 47 36 PM" src="https://user-images.githubusercontent.com/6675724/205788584-12a8b089-6816-47c5-aa33-884770c298b3.png">

    
## (Old testing instructions. Ignore for now)
### Interactive Test    
    conda create --name sketch_animate --file conda-env.txt
    conda activate sketch_animate
    pip install -r requirements.txt flask flask_cors gunicorn ffmpeg-python==0.2.0 shapely==1.7.1 opencv-python
    pip install -e .

    PROJECTROOT=/Users/hjessmith/Projects/AnimatedDrawings  # modify this
    MOTION_CONFIG=${PROJECTROOT}/animate/Data/motion_configs/hip_hop_dancing_interactive.yaml
    CHARACTER_CONFIG=${PROJECTROOT}/animate/Data/Texture/nick_cat.yaml
    cd sketch_animate
    python main.py ${MOTION_CONFIG} ${CHARACTER_CONFIG} .

### Headless Render Test
Create Docker image from Dockerfile

     docker build -t headless_render_test .

Create Docker container with animation code mounted

    docker run -d --platform linux/amd64 --name headless_render_test --mount type=bind,source=${PROJECTROOT}/animate,target=/home/headless_render/code headless_render_test

Get Docker CLI

    docker exec -u headless_render -it headless_render_test bash

Finishing install dependencies from within Docker:

    conda create --name sketch_animate --file conda-env.txt
    conda activate sketch_animate
    pip install -r requirements.txt flask flask_cors gunicorn ffmpeg-python==0.2.0 shapely==1.7.1 opencv-python
    cd code
    pip install -e .

Test headless render:

    ./render_test.sh
