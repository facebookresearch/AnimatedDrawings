from animated_drawings.model.transform import Transform
from animated_drawings.model.vectors import Vectors


class Camera(Transform):

    def __init__(
        self,
        pos: Vectors = Vectors([0.0, 0.0, 0.0]),
        fwd: Vectors = Vectors([0.0, 0.0, 1.0])
    ):
        super().__init__()

        if not isinstance(pos, Vectors):
            pos = Vectors(pos)
        self.set_position(pos)

        if not isinstance(fwd, Vectors):
            fwd = Vectors(fwd)
        self.look_at(fwd)
