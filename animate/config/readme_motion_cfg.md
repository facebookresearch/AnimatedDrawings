# Motion Config File

The contains information about the motion used to drive the Animated Drawing.
Currently, only BVH (BioVision Hierarchy) files are supported, but there is considerable flexibility
regarding the skeleton specified within the BVH (note- only BVH's with one skeleton are supported).

<b>filepath</b> <em>(str)</em>: Path to the BVH file. This can be an absolute path, path relative to the current working directory, or path relative to ${AD_ROOT_DIR}.  

<b>start_frame_idx</b> <em>(int)</em>:
If you want to skip beginning motion frames, this can be set to an int between 0 and `end_frame_idx`, inclusive.

<b>end_frame_idx</b> <em>(int)</em>:
If you want to skip ending motion frames, this can be set to an int between `start_frame_idx+1` and the BVH Frames Count, inclusive.

<b>groundplane_joint</b> <em>(str)</em>:
The name of a joint that exists within the BVH's skeleton.
When visualizing the BVH's motion, the skeleton will have it's worldspace y offset adjusted so this joint is within the y=0 plane at `start_frame_idx`.

<b>forward_perp_joint_vectors</b> <em>(list[List[str, str]])</em>:
During retargeting, it is necessary to compute the 'foward' vector for the skeleton at each frame.
To compute this, we define a series of joint name pairs. 
Each joint name specifies a joint within the BVH skeleton.
For each pair, we compute the normalized vector from the first joint to the second joint.
We then compute the average of these vectors and compute its <em>counter-clockwise</em> perpendicular vectors.
We zero out this vector's y value, and are left with a vector along the xy plane indicating the skeleton's forward vector.

<b>scale</b> <em>(float)</em>:
Uniformly scales the BVH skeleton. 
Useful for visualizing the BVH motion. 
Scaling the skeleton so it fits roughly within a (1, 1, 1) cube will visualize nicely.

<b>up</b> <em>(str)</em>:
The direction corresponding to 'up' within the BVH.
This is used during retargeting, not just BVH motion visualization.
Currently, only `+z` is supported.
