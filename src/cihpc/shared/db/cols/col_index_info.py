#!/bin/python3
# author: Jan Hybs

from typing import List, Dict, Optional

from cihpc.shared.db.timer_index import TimerIndex
from cihpc.shared.db.models import (
    Entity,
    IdEntity,
)


class IndexInfoRun(Entity):
    duration: Optional[float]
    returncode: Optional[int]

    def __init__(self, **kwargs):
        self.duration = None
        self.returncode = None
        super().__init__(**kwargs)

    @property
    def is_broken(self):
        return self.returncode != 0


class ColIndexInfo(IdEntity):
    index: TimerIndex
    run: IndexInfoRun

    def __init__(self, **kwargs):
        self.index = TimerIndex.from_dict(kwargs.pop('index', {}))
        self.run = IndexInfoRun.from_dict(kwargs.pop('run', {}))
        super().__init__(**kwargs)