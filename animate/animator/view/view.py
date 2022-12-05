from abc import abstractmethod


class View:

    def __init__(self, cfg: dict):
        self.cfg: dict = cfg
        pass

    @abstractmethod
    def render(self):
        pass
