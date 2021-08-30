import numpy as np
from Shapes.Shapes import Box
from util import scale, translate



class Light:

    def __init__(self, position=np.array([0.0, 0.0, 0.0], np.float32)):
        self.widget = Box()
        self.model = translate(*position) @ scale(0.1, 0.1, 0.1)

        self.widget.model = self.model @ self.widget.model
        self.widget.points[:,-3:] = 1.0
        self.widget.rebuffer_vertex_data()

        # variables for shader
        self.position = self.model[0:3, -1]
        self.ambient =  np.array([0.4, 0.4, 0.4], np.float32)
        self.diffuse =  np.array([0.4, 0.4, 0.4], np.float32)
        self.specular = np.array([0.4, 0.4, 0.4], np.float32)

    def draw(self, **kwargs):
        self.widget.draw(**kwargs)
