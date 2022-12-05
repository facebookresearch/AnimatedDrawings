from typing import Optional
from sketch_animate.Shapes.BVH import BVH
from sketch_animate.Shapes.ARAP_Sketch import ARAP_Sketch
from model.transform import Transform


class Scene(Transform):
    """
    The scene is the singular 'world' object.
    It contains geometries that need to be drawn, cameras needed to render views, and other objects.
    It keeps track of time.
    It contains references to a shader manager that contains shaders needed to render game objects.
    (maybe this should be a view thing?)
    """

    def __init__(self, cfg: dict):
        super().__init__()

        self.cfg: dict = cfg
        self.bvh: Optional[BVH] = None  # don't think this is needed
        self.sketch: Optional[ARAP_Sketch] = None  # don't think this is needed

    def tick(self):
        pass

    def initialize_time(self):
        pass
