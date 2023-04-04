# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Optional
from abc import abstractmethod


class TimeManager():
    """ Mixin class designed to be used by objects that must keep track of their own time (e.g. time-varying animations) """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._time: float = 0.0  # object's internal time, in seconds
        self._is_paused: bool = False

    def tick(self, delta_t: float) -> None:
        """ Progress objects interal time by delta_t seconds if not paused """
        if not self._is_paused:
            self._time += delta_t
            self.update()

    @abstractmethod
    def update(self):
        """ Contains logic needed to update subclass after tick() """
        pass

    def set_pause(self, pause: Optional[bool]) -> None:
        if pause is None:
            self._is_paused = not self._is_paused
        else:
            self._is_paused = pause

    def set_time(self, time: float) -> None:
        self._time = time

    def get_time(self) -> float:
        return self._time
