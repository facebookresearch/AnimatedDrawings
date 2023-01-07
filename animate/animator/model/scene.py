from animator.model.transform import Transform
from animator.model.time_manager import TimeManager


class Scene(Transform, TimeManager):
    """
    The scene is the singular 'world' object.
    It contains geometries that need to be drawn, cameras needed to render views, and other objects.
    It keeps track of global time.
    It contains references to a shader manager that contains shaders needed to render game objects.
    (maybe this should be a view thing?)
    """

    def __init__(self, cfg: dict):
        super().__init__()
        self.cfg: dict = cfg

    def progress_time(self, delta_t: float) -> None:
        """
        Entry point called to update time in the scene by delta_t seconds.
        Because animatable object within the scene may have their own individual timelines,
        we recurvisely go through objects in the scene and call tick() on each TimeManager.
        """
        self._progress_time(self, delta_t)

    def _progress_time(self, t: Transform, delta_t: float) -> None:
        """ Recursively calls tick() on all TimeManager objects. """

        if isinstance(t, TimeManager):
            t.tick(delta_t)

        for c in t.get_children():
            self._progress_time(c, delta_t)
