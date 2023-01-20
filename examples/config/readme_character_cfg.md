# Character Config File

This configuration file (referred to below as `char_cfg`) contains the information necessary to create an instance of the Animated Drawing class. In additiona the fields below, which are explicitly listed within `char_cfg`, the <em>filepath</em> of `char_cfg` is used to store the location of the character's texture and mask files. Essentally, just make sure the associated `texture.png` and `mask.png` files are in the same directory as `char_cfg`.

<b>height</b> <em>(int)</em>:
Height, in pixels, of `texture.png` and `mask.png` files located in same directory as `char_cfg`.

<b>width</b> <em>(int)</em>:
Width, in pixels, of `texture.png` and `mask.png` files located in same directory as `char_cfg`.

<b>skeleton</b> <em>(list[dict])</em>: List of joints that comprise the character's skeleton. Each joint is a dictionary with the following key:value pairs:

&nbsp;&nbsp;&nbsp;&nbsp; <b>loc</b> <em>(List[int, int])</em>:
The image-space location, in pixels, of the joint. (<em>Note: (0, 0) is top-left corner of image</em>)

&nbsp;&nbsp;&nbsp;&nbsp; <b>name</b> <em>(str)</em>:
The name of the joint.

&nbsp;&nbsp;&nbsp;&nbsp; <b>parent</b> <em>(str)</em>:
The name of the joint's parent joint within the skeletal chain. All joints must have another skeletal joint as their parent, with the exception of the joint named 'root', who's parent must be `null`.

