from animator.model.transform import Transform
from model.vectors import Vectors


class Camera(Transform):

    def __init__(
        self,
        pos: Vectors = Vectors([0.0, 0.0, 0.0]),
        fwd: Vectors = Vectors([0.0, 0.0, 1.0])
    ):
        super().__init__()

        self.set_position(pos)

        self.look_at(fwd)
