# Animated Drawings
This repo contains an implementation of the algorithm described within the paper, `A Method for Automatically Animating Children's Drawings of the Human Figure.' In addition, this repo aims to be a useful creative tool in it's own right, allowing you to flexibly create animations starring your own drawn characters.

## Installation

    git clone https://github.com/facebookresearch/AnimatedDrawings.git
    cd AnimatedDrawings
    pip install -e .

In addition, if you want to automatically rig your own drawings, you'll need to [install torchserve and it's dependencies](https://github.com/pytorch/serve/blob/master/README.md#install-torchserve) 
and [obtain the necessary model weights](./torchserve/model_store/README.md)

## Using Animated Drawings
We provide some example top-level configuration files (or 'mvc_configs') to demonstrate how to run the rendering code.
Scenes are created and rendered according to the parmaeters within the mvc_config.
To see for yourself, run the following python commands from within the AnimatedDrawings root directory:

    from animated_drawings import render

    render.start(./examples/config/mvc/interactive_window_example.yaml)

If everything is installed correctly, an interactive window should appear on your screen. 
(Use space to pause/unpause the scene, arrow keys to move back and forth in time, and q to close the screen.)

<img src='./media/interactive_window_example.gif' width="256" height="256" /> </br></br></br>


Suppose you'd like to save the animation as a video file instead of viewing it directly in a window. Specify a different example mvc_config:

    from animated_drawings import render

    render.start('./examples/config/mvc/export_mp4_example.yaml')

You should see a file, video.mp4, located in the same directory as your script.

<img src='./media/mp4_export_video.gif' width="256" height="256" /> </br></br></br>

Perhaps you'd like a transparent .gif instead of an .mp4? Use this:

    from animated_drawings import render

    render.start('./examples/config/mvc/export_gif_example.yaml')

You'll find video.gif residing within the same directory as your script.

<img src='./media/gif_export_video.gif' width="256" height="256" /> </br></br></br>


### Creating an animation from an image
All of the above examples use drawings with pre-existing annotations.
But suppose you'd like to create an animation starring your own drawing? 
We provide an example script specifically for that purpose.
We use torchserve to pass data to our models, so you'll need to ensure it's properly installed first.
Run the following commands, starting from the AnimatedDrawings root directory:

    # ensure torchserve is running
    cd torchserve
    ./torchserve_start.sh

    cd ../examples
    python image_to_animation.py drawings/garlic.png garlic_out

As you waited, the image located at `drawings/garlic.png` was analyzed, the character detected, segmented, and rigged, and it was animated using BVH motion data from a human actor.
The resulting animation was saved as `./garlic_out/video.gif`.

<img src='./examples/drawings/garlic.png' height="256" /><img src='./media/garlic.gif' width="256" height="256" /></br></br></br>

### Fixing bad predictions
You may notice that, when you ran `python image_to_animation.py drawings/garlic.png garlic_out`, there were addition non-video files within `garlic_out`.
`mask.png`, `texture.png`, and `char_cfg.yaml` contain annotation results of the image character analysis step. These annotations were created from our model predictions.
If the predictions were incorrect, you can manually fix the annotations.
The segmentation mask is a grayscale image that can be edited in Photoshop or Paint.
The skeleton joint locations within char_cfg.yaml can be edited with a text editor (though you'll want to read about the character config parameters within config/README first though.)

Once you've modified annotations, you can render an animation using them like so:

    # run from AnimatedDrawings root directory

    # ensure torchserve is running
    cd torchserve
    ./torchserve_start.sh

    cd ../examples

    # specify the folder where the update animations are located
    python annotations_to_animation.py garlic_out

### Adding multiple characters to scene
Multiple characters can be added to a video by specifying multiple entries within the mvc-config scene's 'ANIMATED_CHARACTERS' list.
To see for yourself, run the following python commands from within the AnimatedDrawings root directory:

    from animated_drawings import render
    render.start('./examples/config/mvc/multiple_characters_example.yaml')
<img src='./examples/characters/char1/texture.png' height="256" /> <img src='./examples/characters/char2/texture.png' height="256" /> <img src='./media/multiple_characters_example.gif' height="256" />

### Adding a background image
Suppose you'd like to add a background to the animation. You can do so by specifying the image path within the config. 
Here's an example:

    from animated_drawings import render

    render.start('./examples/config/mvc/background_example.yaml')

<img src='./examples/characters/char4/texture.png' height="256" /> <img src='./examples/characters/char4/background.png' height="256" /> <img src='./media/background_example.gif' height="256" />

### Adding addition types of motion
You can add your own motion clips as long as they are in BVH format.

Once you have the BVH, you'll need to create an appropriate motion config file and retarget config file.
Once you've done that, you should be good to go. The following code and resulting clip uses a BVH with completely different skeleton.

    from animated_drawings import render

    render.start('./examples/config/mvc/different_bvh_skeleton_example.yaml')


<img src='./media/different_bvh_skeleton_example.gif' height="256" />

### Adding addition character skeletons
To be added later, if requested.

## Creating Your Own Config Files
If you want to create your own config files, see the [configuration file documentation](examples/config/README.md)

## As-Rigid-As-Possible Shape Manipulation

These characters are deformed using [As-Rigid-As-Possible (ARAP) shape manipulation](https://www-ui.is.s.u-tokyo.ac.jp/~takeo/papers/takeo_jgt09_arapFlattening.pdf).
We have a Python implementation of the algorithm, located [here](https://github.com/fairinternal/AnimatedDrawings/blob/main/animated_drawings/model/arap.py), that might be of use to other developers.
