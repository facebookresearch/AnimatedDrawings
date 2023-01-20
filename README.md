# Animated Drawings
This repo contains companion code for the paper, `A Method for Automatically Animating Children's Drawings of the Human Figure.'
In addition, this repo aims to be a useful creative tool in it's own right, allowing you to create your own animated drawings from your own computer. 

## Installation (To be expanded later)
1. create virtual env
2. pip install -e .
3. Install torchserve's java dependency 
4. Obtain .mar files

## Running (To be expanded later)

### Using the Rendering code
We provide a couple of example mvc-level configuration files to demonstrate how to run the rendering code.
Scenes are created and rendered given an *mvc configuration*.
We provide a couple of example, ready-to-go mvc_configs for you to experiment with.
To run one, run the following python commands from within the AnimatedDrawings root directory:

    from animated_drawings import render

    render.start(./examples/config/mvc_interactive_window_example.yaml)

If everything is installed correctly, an interactive window should appear on your screen. 
(Use space to pause/unpause the scene, arrow keys to move back and forth in time, and q to close the screen.)

![interactive_window_example](./media/interactive_window_example.gif)


Suppose you'd like to save the animation as a video file instead of viewing it directly in a window. Specify this config path:

    from animated_drawings import render

    render.start('./examples/config/mvc_export_mp4_example.yaml')

You should see a file, video.mp4, located in the same directory as your script.

Perhaps you'd like a tranparent .GIF instead of an .mp4? Use this:

    from animated_drawings import render

    render.start('./examples/config/mvc_export_gif_example.yaml')

To get an interactive window displaying the animation, run the following code from the AnimatedDrawings root directory
     AnimatedDrawings % python animated_drawings/render.py examples/config/mvc_interactive_window.yaml
- Pass in a config to render.py

### Creating an animation from an image
- Run torchserve script

### Creating a transparent aniamted GIF 
TBD

### Adding multiple characters to scene
TBD

### Adding multiple characters to scene
TBD

### Fixing bad predictions
TBD

### Adding addition types of motion
TBD

### Example outputs and config files
While our torchserve model's don't predict keypoints for non-humanoid skeletons, you could create them manually and create a custom `retarget_cfg` to retarget motion onto its joints.
Likewise, custom `retarget_cfg` files can be written to support non-humanoid BVH skeletons.
Examples to be added in the future.





