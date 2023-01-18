# Retargeter Config File

This file contains the information necessary to apply the motion specified by the motion config onto the Animated Drawing character specified in the character config. Note: below we refer to the BVH actor's skeleton as <em>skeleton</em> and we refer to the Animated Drawing character's rig <em>rig</em> or <em>character rig</em>.


<b>char_starting_location</b> <em>(List[float, float, float])</em>:
The starting xzy position of the character's root.

<b>bvh_projection_bodypart_groups</b> <em>(list[dict])</em>:
The big-picture goal of the retargeter is to use 3D skeletal motion data to drive a 2D character rig.
As part of this process, we project the skeletal joint positions onto 2D planes.
But we don't need to use the same 2D plane for every joint within the skeleton.
Depending upon the motion of particular skeletal bodyparts, it may be preferrable to use different planes (e.g. a <em>frontal</em> projection plane for the skeletal arms and torso, but a <em>saggital</em> projection plane for the legs).
`projection_bodypart_groups` contains a list of bodypart groups, corresponding the BVH skeletal joints which should all be projected onto the same plane. Each bodypart group is a dictionary with the follow key-value pairs:
&nbsp; &nbsp; &nbsp; &nbsp; <b>joint_names</b> <em>(list[str])</em>:
A list containing the names of joints within the BVH skeleton.

&nbsp; &nbsp; &nbsp; &nbsp; <b>name</b> <em>(str)</em>:
A name used to refer to the projection group.

&nbsp; &nbsp; &nbsp; &nbsp; <b>method</b> <em>(str)</em>:
Specifies the projection plane to be used for joints within this group.
Currently, three options supported:

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; `'frontal'`:
Joints are projected onto the frontal plane of the skeleton, as determined by its forward vector.

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; `'saggital'`:
Joints are projected onto the saggital plane of the skeleton, who's normal vector is <em>clockwise</em> perpendicular to the skeleton's forward vector.

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; `'pca'`:
We attempt to automatically choose the best plane (`frontal` or `saggital`) using the following method:

1. Subtract the skeleton root's xy position from each frame, fixing it above the origin.
2. Rotate the skeleton so it's forward vector is facing along the +x axis at each frame.
3. Create a point cloud comprised of the xzy locations of every joint within the bodypart group at every frame. 
4. Perform principal component analysis upon the point cloud. <em>(The first 1st and 2nd components define a projection plane that preserves the maximal variance within the point cloud. The 3rd component defines this plane's normal vector)</em>
5. Take the 3rd component and compute it's cosine similarity to the skeleton's `forward` vector and `saggital` vector. Use the projection plane who's normal vector is more similar to the 3rd component.

<b>char_bodypart_groups</b> <em>(list[dict])</em>:
If there is overlap between the character's torso and its arm, for example, one should be rendered in front of the other. 
But how do we know the order in which to render character bodyparts.
The dictionaries within this list contain information specifying which joints should be rendered together (i.e. during the same pass) and how their 'depth' should be determined. Each dictionary contains the following key-value pairs:

&nbsp; &nbsp; &nbsp; &nbsp;<b>char_joints</b> <em>(list[str])</em>:
A list of names of <em>distal</em> joints of bones within the character rig.
All mesh triangles close to these bones will be rendered on the same pass.

&nbsp; &nbsp; &nbsp; &nbsp;<b>bvh_depth_drivers</b> <em>(list[str])</em>:
But how do we the order in which to render the character bodypart groups?
We do this by computing the distance from one or more skeleton joints (i.e. depth drivers) to their projection planes.
This contains a list of one or more skeleton joints used for this purpose:
the average depth is calculated, then character bodypart groups are rendered from smallest average depth to largest average depth.


<b>char_bvh_root_offset</b> <em>(dict)</em>:
Unless the BVH skeleton starts in the same place for the entirety of motion clip, the root joint of the character rig must be offset to account for the skeleton's translation.
But the proportion of the skeleton and character rig may be very different.
Additionally, the skeleton moves in three dimensions while the character rig is restricted to two dimensions.
The fields within this dicionary are necessary to account for these issues.

&nbsp; &nbsp; &nbsp; &nbsp;<b>bvh_joints</b> <em>(list[list[str]])</em>:
A list of one or more lists of joints defining a series of joint chains within the BVH skeleton (but joints do not need to be directly connected within the BVH skeleton).
We compute the sum of the length of all joint chains; this is used as a heuristic for the <em>scale</em> of the skeleton. We compute a similar heuristic for the character rig, and scale the skeleton's per-frame root offset by the ratio of these values before applying it to the character.

&nbsp; &nbsp; &nbsp; &nbsp;<b>char_joints</b> <em>(list[list[str]])</em>:
A list of one or more lists of joints defining a series of joint chains within the character rig (but joints do not need to be directly connected within the character rig).
We compute the sum of the length of all joint chains; this is used as a heuristic for the <em>scale</em> of the rig. We compute a similar heuristic for the BVH skeleton, and scale the skeleton's per-frame root offset by the ratio of these values before applying it to the character.

&nbsp; &nbsp; &nbsp; &nbsp;<b>bvh_projection_bodypart_group_for_offset</b> <em>(str)</em>:
The skeleton root position offsets must be projected onto a 2D plane prior to being used to translate the character rig.
But which plane should be used?
Ideally, this is the same plane as the BVH skeleton party group responsible for translating the skeleton (often this is the legs).
Therefore, this is the `name` of a `bvh_projection_bodypart_group`: whichever plane this bvh_bodypart_group is projected onto will also be used for the root offset.

<b>char_joint_bvh_joints_mapping</b> <em>(dict[str, List[str, str]])</em>:
To retarget a skeletal pose onto a character rig, we rotate the bones of the rig such that their global orientations within the 2D plane matches the global orientations of corresponding joints from the BVH skeleton after projections onto a 2D plane.
This dictionary defines a set of mappings between a character rig joint and a set of 2 BVH skeleton joints.
The dictionary keys are strings specifying the names of character rig joints.
At each frame, the character rig's <em>bone</em> (whose distal joint name is specified by the key) is rotated to match the orientation of the vector from the first BVH skeletal joints to the second BVH skeletal joint.
Note: the 2 BVH joints do not need to be directly connected within the BVH skeleton.
