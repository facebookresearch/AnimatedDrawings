# Configuration Files

There are four different types of configuration files:
- MVC Configuration Files
- Character Configuration Files
- Motion Configuration Files
- Retarget Configuration Files


## <a name="mvc"></a>MVC Config File
This is the top-level configuration file, passed into `render.start()` to generate the animation. All parameters and options not specifically related to the Animated Drawing character, the BVH file, or the retargeting process go in here.
Such parameters belong to one of three subgroups, in alignment with the Model-View-Controller design pattern. (Note: the 'Model' element of MVC is referred to as 'scene')
Most of the available parameters are defined in [animated_drawings/mvc_base_cfg.yaml](../../animated_drawings/mvc_base_cfg.yaml). This file should **not** be changed. Instead, create a new mvc config file containing *only* the parameters that need to be modified.
The rendering script will read the initial parameters from `mvc_base_cfg.yaml` and overwrite any parameters specified within the new mvc config file. 
See the [example mvc config files](mvc) for examples.

- <b>scene</b> <em>(dict)</em>: Dictionary containing parameters used by the MVC's Model/Scene component.

    - <b>ADD_FLOOR</b> <em>(bool)</em>: If `True`, a floor will be added to the scene and rendered.

    - <b>ADD_AD_RETARGET_BVH</b> <em>(bool)</em>: If `True`, a visualization of the original BVH motion driving the Animated Drawing characters will be added to the scene.

    - <b>ANIMATED_CHARACTERS</b> <em>List[dict[str:str, str:str, str:str]]</em>:
 A list of dictionaries containing the filepaths of config files necessary to create and animated an Animated Drawing character. 
 Add more dictionaries to add more characters into a scene.
Contains the following key-value pairs:

        - <b>character_cfg</b> <em>(str)</em>: Path to the character config file.

        - <b>motion_cfg</b> <em>(str)</em>: Path to the motion config file.

        - <b>retarget_cfg</b> <em>(str)</em>: Path to the retarget config file.

- <b>view</b> <em>(dict)</em>: Dictionary containing parameters used by the MVC's View component.

    - <b>CLEAR_COLOR</b> <em>(List[float, float, float, float])</em>: 0-1 float values indicating RGBA clear color (i.e. background color).

    - <b>WINDOW_DIMENSIONS</b> <em>(List[int, int])</em>: Width, height (in pixels) of the window or output video file.

    - <b>DRAW_AD_RIG</b> <em>(bool)</em>: If `True`, renders the rig used to deform the Animated Drawings Mesh. Hides it otherwise.

    - <b>DRAW_AD_TXTR</b> <em>(bool)</em>: If `True`, renders the texture of the Animated Drawings character. Hides it otherwise.

    - <b>DRAW_AD_COLOR</b> <em>(bool)</em>: If `True`, renders the Animated Drawings mesh using per-joint colors instead of the original texture. Hides this otherwise.

    - <b>DRAW_AD_MESH_LINES</b> <em>(bool)</em>: If `True`, renders the Animated Drawings mesh edges. Hides this otherwise.

    - <b>CAMERA_POS</b> <em>(List[float, float, float])</em>: The xyz position of the camera used to render the scene.

    - <b>CAMERA_FWD</b> <em>(List[float, float, float])</em>: The vector used to define the 'foward' orientation of the camera.

    - <b>USE_MESA</b> <em>(bool)</em>: If `True`, will attempt to use osmesa to to render the scene directly to a file without requiring a window.
Necessary for headless video rendering.  
This cannot be used if using an `interactive` mode controller.

    - <b>BACKGROUND_IMAGE</b> <em>(str)</em>: Path to an image to use for the video background. Will be stretched to fit WINDOW_DIMENSIONS.

- <b>controller</b> <em>(dict)</em>: Dictionary containing parameters used by the MVC's Controller component.

    - <b>MODE</b> <em>(str)</em>: Specifies the 'mode' of the controller.
If set to `'interactive'`, scene is rendered into an interactive window with a movable camera, pause-able scene, and arrows that progress and rewind time.
Cannot be used when `view['USE_MESA']` is `True`.
If set to `video_render`, renders the video directly to file.
The window, if it appears, is non-interactive.

    - <b>KEYBOARD_TIMESTEP</b> <em>(float)</em>: The number of seconds to step forward/backward using left/right arrow keys. 
Only used in `interactive` mode.

    - <b>OUTPUT_VIDEO_PATH</b> <em>(str)</em>: The full filepath where the output video will be saved. 
Only used in `video_render` mode.
Currently, only `.gif` and `.mp4` video formats are supported. 
Transparency is only available for `.gif` videos.


    - <b>OUTPUT_VIDEO_CODEC</b> <em>(str)</em>: 
The codec to use when encoding the output video.
Only used in `video_render` mode and only if a `.mp4` output video file is specified.

## <a name="character"></a>Character Config File

This configuration file (referred to below as `char_cfg`) contains the information necessary to create an instance of the Animated Drawing class. In addition to the fields below, which are explicitly listed within `char_cfg`, the <em>filepath</em> of `char_cfg` is used to store the location of the character's texture and mask files. Essentially, just make sure the associated `texture.png` and `mask.png` files are in the same directory as `char_cfg`.

- <b>height</b> <em>(int)</em>:
Height, in pixels, of `texture.png` and `mask.png` files located in same directory as `char_cfg`.

- <b>width</b> <em>(int)</em>:
Width, in pixels, of `texture.png` and `mask.png` files located in same directory as `char_cfg`.

- <b>skeleton</b> <em>(list[dict])</em>: List of joints that comprise the character's skeleton. Each joint is a dictionary with the following key:value pairs:

    - <b>loc</b> <em>(List[int, int])</em>:
The image-space location, in pixels, of the joint. (<em>Note: (0, 0) is top-left corner of image</em>)

    - <b>name</b> <em>(str)</em>:
The name of the joint.

    - <b>parent</b> <em>(str)</em>:
The name of the joint's parent joint within the skeletal chain. All joints must have another skeletal joint as their parent, with the exception of the joint named 'root', who's parent must be `null`.


## <a name="motion"></a>Motion Config File

This contains information about the motion used to drive the Animated Drawing.
Currently, only BVH (BioVision Hierarchy) files are supported, but there is considerable flexibility
regarding the skeleton specified within the BVH (note- only BVH's with one skeleton are supported).

- <b>filepath</b> <em>(str)</em>: Path to the BVH file. This can be an absolute path, path relative to the current working directory, or path relative the AnimatedDrawings root directory.

- <b>start_frame_idx</b> <em>(int)</em>:
If you want to skip beginning motion frames, this can be set to an int between 0 and `end_frame_idx`, inclusive.

- <b>end_frame_idx</b> <em>(int)</em>:
If you want to skip ending motion frames, this can be set to an int between `start_frame_idx+1` and the BVH Frames Count, inclusive.

- <b>frame_time</b> <em>(float)</em>: 
If you want to override the frame time specified within the BVH, you can set it here.

- <b>groundplane_joint</b> <em>(str)</em>:
The name of a joint that exists within the BVH's skeleton.
When visualizing the BVH's motion, the skeleton will have it's worldspace y offset adjusted so this joint is within the y=0 plane at `start_frame_idx`.

- <b>forward_perp_joint_vectors</b> <em>(list[List[str, str]])</em>:
During retargeting, it is necessary to compute the 'foward' vector for the skeleton at each frame.
To compute this, we define a series of joint name pairs. 
Each joint name specifies a joint within the BVH skeleton.
For each pair, we compute the normalized vector from the first joint to the second joint.
We then compute the average of these vectors and compute its <em>counter-clockwise</em> perpendicular vector.
We zero out this vector's y value, and are left with a vector along an xz plane indicating the skeleton's forward vector.

- <b>scale</b> <em>(float)</em>:
Uniformly scales the BVH skeleton. 
Useful for visualizing the BVH motion. 
Scaling the skeleton so it fits roughly within a (1, 1, 1) cube will visualize nicely.

- <b>up</b> <em>(str)</em>:
The direction corresponding to 'up' within the BVH.
This is used during retargeting, not just BVH motion visualization.
Currently, only `+y` and `+z` are supported.

## <a name="retarget"></a>Retarget Config File

This file contains the information necessary to apply the motion specified by the motion config onto the Animated Drawing character specified in the character config. Note: below we refer to the BVH actor's skeleton as <em>skeleton</em> and we refer to the Animated Drawing character's rig as <em>rig</em> or <em>character rig</em>.

- <b>char_starting_location</b> <em>(List[float, float, float])</em>:
The starting xzy position of the character's root.

- <b>bvh_projection_bodypart_groups</b> <em>(list[dict])</em>:
The big-picture goal of the retargeter is to use 3D skeletal motion data to drive a 2D character rig.
As part of this process, we project the skeletal joint positions onto 2D planes.
But we don't need to use the same 2D plane for every joint within the skeleton.
Depending upon the motion of particular skeletal bodyparts, it may be preferable to use different planes (e.g. a <em>frontal</em> projection plane for the skeletal arms and torso, but a <em>sagittal</em> projection plane for the legs).
`projection_bodypart_groups` contains a list of bodypart groups, corresponding the BVH skeletal joints which should all be projected onto the same plane. Each bodypart group is a dictionary with the follow key-value pairs:

    - <b>bvh_joint_names</b> <em>(list[str])</em>:
A list containing the names of joints within the BVH skeleton.

    - <b>name</b> <em>(str)</em>:
A name used to refer to the projection group.

    - <b>method</b> <em>(str)</em>:
Specifies the projection plane to be used for joints within this group.
Currently, three options supported:

        - `'frontal'`:
Joints are projected onto the frontal plane of the skeleton, as determined by its forward vector.

        - `'sagittal'`:
Joints are projected onto the sagittal plane of the skeleton, who's normal vector is <em>clockwise</em> perpendicular to the skeleton's forward vector.

        - `'pca'`:
We attempt to automatically choose the best plane (`frontal` or `sagittal`) using the following method:

            1. Subtract the skeleton root's xy position from each frame, fixing it above the origin.
            2. Rotate the skeleton so it's forward vector is facing along the +x axis at each frame.
            3. Create a point cloud comprised of the xzy locations of every joint within the bodypart group at every frame. 
            4. Perform principal component analysis upon the point cloud. <em>(The first 1st and 2nd components define a projection plane that preserves the maximal variance within the point cloud. The 3rd component defines this plane's normal vector)</em>
            5. Take the 3rd component and compute it's cosine similarity to the skeleton's `forward` vector and `sagittal` vector. Use the projection plane who's normal vector is more similar to the 3rd component.

- <b>char_bodypart_groups</b> <em>(list[dict])</em>:
If there is overlap between the character's torso and its arm, for example, one should be rendered in front of the other. 
But how do we know the order in which to render character bodyparts.
The dictionaries within this list contain information specifying which joints should be rendered together (i.e. during the same pass) and how their 'depth' should be determined. Each dictionary contains the following key-value pairs:

    - <b>char_joints</b> <em>(list[str])</em>:
A list of names of <em>distal</em> joints of bones within the character rig.
All mesh triangles close to these bones will be rendered on the same pass.

    - <b>bvh_depth_drivers</b> <em>(list[str])</em>:
But how do we the order in which to render the character bodypart groups?
We do this by computing the distance from one or more skeleton joints (i.e. depth drivers) to their projection planes.
This contains a list of one or more skeleton joints used for this purpose:
the average depth is calculated, then character bodypart groups are rendered from smallest average depth to largest average depth.

- <b>char_bvh_root_offset</b> <em>(dict)</em>:
Unless the BVH skeleton stands in the same place for the entirety of motion clip, the root joint of the character rig must be offset to account for the skeleton's translation.
But the proportion of the skeleton and character rig may be very different.
Additionally, the skeleton moves in three dimensions while the character rig is restricted to two dimensions.
The fields within this dictionary are necessary to account for these issues.

    - <b>bvh_joints</b> <em>(list[list[str]])</em>:
A list of one or more lists of joints defining a series of joint chains within the BVH skeleton (but joints do not need to be directly connected within the BVH skeleton).
We compute the sum of the length of all joint chains; this is used as a heuristic for the <em>scale</em> of the skeleton. We compute a similar heuristic for the character rig, and scale the skeleton's per-frame root offset by the ratio of these values before applying it to the character.

    - <b>char_joints</b> <em>(list[list[str]])</em>:
A list of one or more lists of joints defining a series of joint chains within the character rig (but joints do not need to be directly connected within the character rig).
We compute the sum of the length of all joint chains; this is used as a heuristic for the <em>scale</em> of the rig. We compute a similar heuristic for the BVH skeleton, and scale the skeleton's per-frame root offset by the ratio of these values before applying it to the character.

    - <b>bvh_projection_bodypart_group_for_offset</b> <em>(str)</em>:
The skeleton root position offsets must be projected onto a 2D plane prior to being used to translate the character rig.
But which plane should be used?
Ideally, this is the same plane as the BVH skeleton projection bodypart group responsible for translating the skeleton (often this is the legs).
Therefore, this is the `name` of a `bvh_projection_bodypart_group`: whichever plane this bvh_bodypart_group is projected onto will also be used for the root offset.

- <b>char_joint_bvh_joints_mapping</b> <em>(dict[str, List[str, str]])</em>:
To retarget a skeletal pose onto a character rig, we rotate the bones of the rig such that their global orientations within the 2D plane matches the global orientations of corresponding joints from the BVH skeleton after projections onto a 2D plane.
This dictionary defines a set of mappings between a character rig joint and a set of 2 BVH skeleton joints.
The dictionary keys are strings specifying the names of character rig joints.
At each frame, the character rig's <em>bone</em> (whose distal joint name is specified by the key) is rotated to match the orientation of the vector from the first BVH skeletal joints to the second BVH skeletal joint.
Note: the 2 BVH joints do not need to be directly connected within the BVH skeleton.

- <b>char_runtime_checks</b> <em>(list[list[str]])</em>:
Depending upon the pose the character is drawn in, sometimes it's better to remove elements from `char_joint_bvh_joints_mapping`.
The most frequent example of this occurs when <em>tadpole</em> people are drawn- characters in which the torso and the head are essentially the same.
For such characters, the 'neck' of the character, as drawn, essentially points downward.
When the neck is rotated to match the orientation of a human skeleton, this flips the character's face, producing poor results.
For situations like this, you can specify runtime checks to do once the starting pose of the drawn character is known.
Each item in the list is its own check to run; the first item in the list is the type of test to run, and the other list items are the parameters it needs.
Currently, only `above` test is supported. 
In this test, the second element is the name of a <em>target joint</em>, and the third and fourth elements are the names of <em>reference joints</em>.
If the target joint is not `above` the vector from the first to the second reference joint, it is removed. 
