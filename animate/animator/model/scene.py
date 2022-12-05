from typing import Optional
from sketch_animate.Shapes.BVH import BVH
from sketch_animate.Shapes.ARAP_Sketch import ARAP_Sketch
from model.transform import Transform
from model.camera import Camera

from sketch_animate.Shaders.Shader import Shader  # this should probably go into view
from OpenGL import GL  # this should probably go into view
import numpy as np  # this should probably go into view


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

        # this should probably go into view
        self.shaders = {}
        self.shader_ids = {}
        self.prep_shaders()

    def tick(self):
        pass

    def initialize_time(self):
        pass


    # this should probably go into view
    def prep_shaders(self):

        BVH_VERT = "/Users/hjessmith/Projects/AnimatedDrawings/animate/sketch_animate/Shaders/bvh.vert"
        BVH_FRAG = "/Users/hjessmith/Projects/AnimatedDrawings/animate/sketch_animate/Shaders/bvh.frag"
        self._initiatize_shader('bvh_shader', BVH_VERT, BVH_FRAG)

        COLOR_VERT = "/Users/hjessmith/Projects/AnimatedDrawings/animate/sketch_animate/Shaders/color.vert"
        COLOR_FRAG = "/Users/hjessmith/Projects/AnimatedDrawings/animate/sketch_animate/Shaders/color.frag"
        self._initiatize_shader('color_shader', COLOR_VERT, COLOR_FRAG)

        TEXTURE_VERT = "/Users/hjessmith/Projects/AnimatedDrawings/animate/sketch_animate/Shaders/texture.vert"
        TEXTURE_FRAG = "/Users/hjessmith/Projects/AnimatedDrawings/animate/sketch_animate/Shaders/texture.frag"
        self._initiatize_shader(
            'texture_shader', TEXTURE_VERT, TEXTURE_FRAG, texture=True)

        # GLYPH_VERT = "/Users/hjessmith/Projects/AnimatedDrawings/animate/sketch_animate/Shaders/glyph.vert"
        # GLYPH_FRAG = "/Users/hjessmith/Projects/AnimatedDrawings/animate/sketch_animate/Shaders/glyph.frag"
        # self._initiatize_shader('glyph_shader', GLYPH_VERT, GLYPH_FRAG)

        # BORDER_VERT = "/Users/hjessmith/Projects/AnimatedDrawings/animate./sketch_animate/Shaders/border.vert"
        # BORDER_FRAG = "/Users/hjessmith/Projects/AnimatedDrawings/animate/sketch_animate/Shaders/border.frag"
        # self._initiatize_shader('border_shader', BORDER_VERT, BORDER_FRAG)

        # POINTCLOUD_VERT = "/Users/hjessmith/Projects/AnimatedDrawings/animate/sketch_animate/Shaders/pointcloud.vert"
        # POINTCLOUD_FRAG = "/Users/hjessmith/Projects/AnimatedDrawings/animate/sketch_animate/Shaders/pointcloud.frag"
        # self._initiatize_shader('pointcloud_shader', POINTCLOUD_VERT, POINTCLOUD_FRAG)

        # VECTOR_VERT = "/Users/hjessmith/Projects/AnimatedDrawings/animate/sketch_animate/Shaders/vector.vert"
        # VECTOR_FRAG = "/Users/hjessmith/Projects/AnimatedDrawings/animate/sketch_animate/Shaders/vector.frag"
        # self._initiatize_shader('vector_shader', VECTOR_VERT, VECTOR_FRAG)

        # BONE_ASSIGN_VERT = "/Users/hjessmith/Projects/AnimatedDrawings/animate/sketch_animate/Shaders/bone_assignment.vert"
        # BONE_ASSIGN_FRAG = "/Users/hjessmith/Projects/AnimatedDrawings/animate/sketch_animate/Shaders/bone_assignment.frag"
        # self._initiatize_shader('bone_assignment', BONE_ASSIGN_VERT, BONE_ASSIGN_FRAG)

    # this should probably go into view
    def update_shaders_view_transform(self, camera: Camera):
        # Update each shader with the transform for this viewer's camera
        view_transform: Transform = camera.transform
        #view_pos = self.camera_manager.get_camera_position(camera)
        for key in self.shader_ids:
            GL.glUseProgram(self.shader_ids[key])
            view_loc = GL.glGetUniformLocation(self.shader_ids[key], "view")
            GL.glUniformMatrix4fv(view_loc, 1, GL.GL_FALSE, view_transform.T)
            viewPos_loc = GL.glGetUniformLocation(
                self.shader_ids[key], "viewPos")
            GL.glUniform3fv(viewPos_loc, 1, view_transform[-1:,:-1])

    # this should probably go into view
    def _set_shader_projections(self, proj_m: np.ndarray):
        for shader in self.shader_ids.values():
            GL.glUseProgram(shader)
            proj_loc = GL.glGetUniformLocation(shader, "proj")
            GL.glUniformMatrix4fv(proj_loc, 1, GL.GL_FALSE, proj_m.T)

    # this should probably go into view
    def _initiatize_shader(self, shader_name: str, vert_path: str, frag_path: str, texture=False, light=False):
        self.shaders[shader_name] = Shader(vert_path, frag_path)
        self.shader_ids[shader_name] = self.shaders[shader_name].glid

        if texture:
            GL.glUseProgram(self.shader_ids[shader_name])
            GL.glUniform1i(GL.glGetUniformLocation(
                self.shader_ids[shader_name], 'texture0'), 0)
