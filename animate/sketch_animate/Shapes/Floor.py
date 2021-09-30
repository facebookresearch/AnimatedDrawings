from Shapes.Shapes import Rectangle
from util import rotate, translate


class Floor:

    def __init__(self):
        self.tiles = []
        for idx in range(-5, 6):
            for jdx in range(-5, 6):
                if (idx + jdx) % 2:
                    color = 'white'
                else:
                    #color = 'black'
                    color = [0.9, 0.9, 0.9]
                tile = Rectangle(color=color)
                tile.model = rotate([1.0,0.0,0.0], -90.0) @ tile.model
                tile.model = translate(float(idx), -0.1, float(jdx)) @ tile.model
                self.tiles.append(tile)

    def draw(self, **kwargs):
        for tile in self.tiles:
            tile.draw(**kwargs)
