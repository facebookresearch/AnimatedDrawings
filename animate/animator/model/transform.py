from __future__ import annotations  # so we can refer to class Type inside class
import numpy as np
from model.vectors import Vectors
from model.quaternions import Quaternions
import logging
import ctypes
from typing import Union, Optional, List
import OpenGL.GL as GL


class Transform():
    """Base class from which all other scene objects descend"""

    def __init__(self, parent: Optional[Transform] = None, name: Optional[str] = None):
        self.parent: Optional[Transform] = parent
        self.children: List[Transform] = []

        self._name: Optional[str] = name

        # TODO: make all of these hidden
        self.rotate_m: np.ndarray = np.identity(4, dtype=np.float32)
        self.translate_m: np.ndarray = np.identity(4, dtype=np.float32)
        self.scale_m: np.ndarray = np.identity(4, dtype=np.float32)

        self.local_transform: np.ndarray = np.identity(4, dtype=np.float32)
        self.world_transform: np.ndarray = np.identity(4, dtype=np.float32)
        self.dirty_bit: bool = True  # are world/local transforms stale?

    def update_transforms(self, parent_dirty_bit: bool = False) -> None:
        """
        Updates transforms if stale.
        If own dirty bit is set, recompute local matrix
        If own or parent's dirty bit is set, recompute world matrix
        If own or parent's dirty bit is set, recurse on children
        Set dirty bit back to false.
        """
        if self.dirty_bit:
            self.compute_local_transform()
        if self.dirty_bit | parent_dirty_bit:
            self.compute_world_transform()

        for c in self.children:
            c.update_transforms(self.dirty_bit | parent_dirty_bit)

        self.dirty_bit = False

    def compute_local_transform(self) -> None:
        self.local_transform = self.translate_m @ self.rotate_m @ self.scale_m

    def compute_world_transform(self) -> None:
        self.world_transform = self.local_transform
        if self.parent:
            self.world_transform = self.parent.world_transform @ self.world_transform

    def set_position(self, pos: Union[np.ndarray, Vectors]) -> None:
        """ Set the absolute values of the translational elements of transform """
        if isinstance(pos, Vectors):
            pos = pos.vs

        if pos.shape == (1, 3):
            pos = np.squeeze(pos)
        elif pos.shape == (3,):
            pass
        else:
            msg = f'bad vector dim passed to set_position. Found: {pos.shape}'
            logging.critical(msg)
            assert False, msg

        self.translate_m[:-1, -1] = pos
        self.dirty_bit = True

    def get_local_position(self) -> np.ndarray:
        """ Ensure local transform is up-to-date and return local xyz coordinates """
        if self.dirty_bit:
            self.compute_local_transform()
        return np.copy(self.local_transform[:-1, -1])

    def get_world_position(self) -> np.ndarray:
        """ Ensure all parent transforms are update and return world xyz coordinates """

        if self.parent is None:
            self.update_transforms()
        else:
            ancestor: Transform = self.parent
            while ancestor.parent is not None:
                ancestor = ancestor.parent
            ancestor.update_transforms()
        return np.copy(self.world_transform[:-1, -1])

    def offset(self, pos: Union[np.ndarray, Vectors]) -> None:
        """ Translational offset by the specified amount """
        if isinstance(pos, Vectors):
            pos = pos.vs
        self.set_position(self.translate_m[:-1, -1] + pos)

    def look_at(self, fwd_: Union[np.ndarray, Vectors]) -> None:
        """Given a forward vector, rotate the transform to face that position"""
        if isinstance(fwd_, np.ndarray):
            fwd_ = Vectors(fwd_)
        fwd: Vectors = fwd_.copy()  # norming will change the vector

        if fwd.vs.shape != (1, 3):
            logging.critical(
                f'look_at fwd_ vector must have shape [1,3]. Found: {fwd.vs.shape}')
            assert False

        tmp: Vectors = Vectors([0.0, 1.0, 0.0])

        # if fwd and tmp are same vector, modify tmp to avoid collapse
        if np.isclose(fwd.vs, tmp.vs).all() or np.isclose(fwd.vs, -tmp.vs).all():
            tmp.vs[0] += 0.001

        right: Vectors = tmp.cross(fwd)
        up: Vectors = fwd.cross(right)

        fwd.norm()
        right.norm()
        up.norm()

        rotate_m = np.identity(4)
        rotate_m[:-1, 0] = np.squeeze(right.vs)
        rotate_m[:-1, 1] = np.squeeze(up.vs)
        rotate_m[:-1, 2] = np.squeeze(fwd.vs)

        self.rotate_m = rotate_m
        self.dirty_bit = True

    def set_rotate(self, q: Quaternions) -> None:
        if q.qs.shape != (1, 4):
            msg = f'set_rotate q must have dimension (1, 4). Found: {q.qs.shape}'
            logging.critical(msg)
            assert False, msg

        self.rotate_m = q.to_rotation_matrix()
        self.dirty_bit = True

    def add_child(self, child: Transform) -> None:
        self.children.append(child)
        child.set_parent(self)

    def set_parent(self, parent: Transform) -> None:
        self.parent = parent
        self.dirty_bit = True

    def draw(self, recurse=True, **kwargs) -> None:
        """ Draw this transform and recurse on children """
        self._draw(**kwargs)

        if recurse:
            for child in self.children:
                child.draw(**kwargs)
            #[child.draw(**kwargs) for child in self.children]

    def _draw(self, **kwargs):
        """Transforms default to not being drawn. Subclasses must implement how they appear"""
        pass


class TransformWidget(Transform):
    def __init__(self, shader_name='color_shader'):

        super().__init__()

        self.points: np.ndarray = np.array([
            [0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            [0.0, 1.0, 0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
            [0.0, 0.0, 1.0, 0.0, 0.0, 1.0],
        ], np.float32)

        self.shader_name: str = shader_name

        self._is_opengl_initialized: bool = False

    def _initialize_opengl_resources(self):
        self.vao = GL.glGenVertexArrays(1)
        self.vbo = GL.glGenBuffers(1)

        GL.glBindVertexArray(self.vao)

        # buffer vertex data
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.points, GL.GL_STATIC_DRAW)

        vert_bytes = 4 * self.points.shape[1]  # 4 is byte size of np.float32

        pos_offset = 4 * 0
        color_offset = 4 * 3

        # position attributes
        GL.glVertexAttribPointer(
            0, 3, GL.GL_FLOAT, False, vert_bytes, ctypes.c_void_p(pos_offset))
        GL.glEnableVertexAttribArray(0)

        # color attributes
        GL.glVertexAttribPointer(
            1, 3, GL.GL_FLOAT, False, vert_bytes, ctypes.c_void_p(color_offset))
        GL.glEnableVertexAttribArray(1)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        self._is_opengl_initialized = True

    def _draw(self, **kwargs):

        if not self._is_opengl_initialized:
            self._initialize_opengl_resources()

        GL.glUseProgram(kwargs['shader_ids'][self.shader_name])
        model_loc = GL.glGetUniformLocation(
            kwargs['shader_ids'][self.shader_name], "model")
        GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE,
                              self.world_transform.T)

        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_LINES, 0, len(self.points))
        GL.glBindVertexArray(0)
        
