from animator.model.transform import Transform
from model.vector import Vector


class Camera(Transform):

    def __init__(
        self,
        pos: Vector = Vector(0.0, 0.0, 0.0),
        fwd: Vector = Vector(0.0, 0.0, 1.0)
    ):
        super().__init__()

        self.set_position(pos)

        self.look_at(fwd)
