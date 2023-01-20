# MVC Config File
This configuration file contains all the parameters and options not specified related to the Animated Drawing character, the BVH file, or the retargeting process.
Such parameters belong to one of three subgroups, in alignment with the Model-View-Controller design pattern. (Note: the 'Model' element of MVC is referred to as 'scene')
Most of the available parameters are defined in `mvc_base_cfg.yaml`. This file should **not** be changed. Instead, create a new mvc config file containg *only* the parameters that need to be modified.
The rendering script will read the initial parameters from `mvc_base_cfg.yaml` and overwrite any parameters specified within the new mvc config file. 
See `mvc_interactive_window.yaml`, `mvc_headless_video_export.yaml`, or `mvc_window_video_export.yaml` for examples.

<b>scene</b> <em>(dict)</em>: Dictionary containing parameters used by the MVC's Model/Scene component.

&nbsp; &nbsp; &nbsp; &nbsp;<b>ADD_FLOOR</b> <em>(bool)</em>: If `True`, a floor will be added to the scene and rendered.

&nbsp; &nbsp; &nbsp; &nbsp; <b>ADD_AD_RETARGET_BVH</b> <em>(bool)</em>: If `True`, a visualization of the original BVH motion driving hte Animated Drawing characters will be added to the scene.

&nbsp; &nbsp; &nbsp; &nbsp; <b>ANIMATED_CHARACTERS</b> <em>List[dict[str:str, str:str, str:str]]</em>:
 A list of dictionaries containing the filepaths of config files necessary to create and animated an Animated Drawing character. 
 Add more dictionaries to add more characters into a scene.
Contains the following key-value pairs:

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <b>character_cfg</b> <em>(str)</em>: Path to the character config file.

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <b>motion_cfg</b> <em>(str)</em>: Path to the motion config file.

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <b>retarget_cfg</b> <em>(str)</em>: Path to the retarget config file.

<b>view</b> <em>(dict)</em>: Dictionary containing parameters used by the MVC's View component.

&nbsp; &nbsp; &nbsp; &nbsp; <b>CLEAR_COLOR</b> <em>(List[float, float, float, float])</em>: 0-1 float values indicating RGBA clear color (i.e. background color).

&nbsp; &nbsp; &nbsp; &nbsp; <b>WINDOW_DIMENSIONS</b> <em>(List[int, int])</em>: Width, height (in pixels) of the window or output video file.

&nbsp; &nbsp; &nbsp; &nbsp; <b>DRAW_AD_RIG</b> <em>(bool)</em>: If `True`, renders the rig used to deform the Animated Drawings Mesh. Hides it otherwise.

&nbsp; &nbsp; &nbsp; &nbsp; <b>DRAW_AD_TXTR</b> <em>(bool)</em>: If `True`, renders the texture of the Animated Drawings character. Hides it otherwise.

&nbsp; &nbsp; &nbsp; &nbsp; <b>DRAW_AD_COLOR</b> <em>(bool)</em>: If `True`, renders the Animated Drawings mesh using per-joint colors instead of the original texture. Hides this otherwise.

&nbsp; &nbsp; &nbsp; &nbsp; <b>DRAW_AD_MESH_LINES</b> <em>(bool)</em>: If `True`, renders the Animated Drawings mesh edges. Hides this otherwise.

&nbsp; &nbsp; &nbsp; &nbsp; <b>CAMERA_POS</b> <em>(List[float, float, float])</em>: The xyz position of the camera used to render the scene.

&nbsp; &nbsp; &nbsp; &nbsp; <b>CAMERA_FWD</b> <em>(List[float, float, float])</em>: The vector used to define the 'foward' orientation of the camera.

&nbsp; &nbsp; &nbsp; &nbsp; <b>USE_MESA</b> <em>(bool)</em>: If `True`, will attempt to use osmesa to to render the scene directly to a file without requiring a window.
Necessary for headless video rendering.  
This cannot be used if using an `interactive` mode controller.

&nbsp; &nbsp; &nbsp; &nbsp; <b>BACKGROUND_IMAGE</b> <em>(str)</em>: Path to an image to use for the video background. Will be stretched to fit WINDOW_DIMENSIONS.

<b>controller</b> <em>(dict)</em>: Dictionary containing parameters used by the MVC's Controller component.

&nbsp; &nbsp; &nbsp; &nbsp; <b>MODE</b> <em>(str)</em>: Specifies the 'mode' of the controller.
If set to `'interactive'`, scene is rendered into an interactive window with a movable camera, pause-able scene, and arrows that progress and rewind time.
Cannot be used when `view['USE_MESA']` is `True`.
If set to `video_render`, renders the video directly to file.
The window, if it appears, is non-interactive.

&nbsp; &nbsp; &nbsp; &nbsp; <b>KEYBOARD_TIMESTEP</b> <em>(float)</em>: The number of seconds to step forward/backward using left/right arrow keys. 
Only used in `interactive` mode.

&nbsp; &nbsp; &nbsp; &nbsp; <b>OUTPUT_VIDEO_PATH</b> <em>(str)</em>: The full filepath where the output video will be saved. 
Only used in `video_render` mode.
Currently, only `.gif` and `.mp4` video formats are supported. 
Transparency is only available for `.gif` videos.


&nbsp; &nbsp; &nbsp; &nbsp; <b>OUTPUT_VIDEO_CODEC</b> <em>(str)</em>: 
The codec to use when encoding the output video.
Only used in `video_render` mode and only if a `.mp4` output video file is specified.