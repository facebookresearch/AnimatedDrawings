from abc import abstractmethod


class View:
    """
    Base View class which all other Views must be derived.
    Views are responsible for controlling what is and isn't visible to them.
    Views are responsible for initiating the 'draw' methods for each object which they want to render.
    """

    def __init__(self, cfg: dict):
        self.cfg: dict = cfg
        pass

    @abstractmethod
    def render(self):
        pass
