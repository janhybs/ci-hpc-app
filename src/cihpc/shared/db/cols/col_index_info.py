#!/bin/python3
# author: Jan Hybs

import time
from itertools import groupby
from typing import List, Dict, Optional

from cihpc.shared.db.timer_index import TimerIndex
from cihpc.shared.db.models import (
    Entity,
    IdEntity,
)


class IndexInfoRun(Entity):
    is_broken: Optional[bool]
    timestamp: Optional[float]
    returncode: Optional[int]

    def __init__(self, **kwargs):
        self.timestamp = float(kwargs.pop('timestamp', time.time()))
        self.is_broken = None
        self.returncode = None
        super().__init__(**kwargs)


class ColIndexInfo(IdEntity):
    index: TimerIndex
    run: IndexInfoRun

    def __init__(self, **kwargs):
        self.index = TimerIndex.from_dict(kwargs.pop('index', {}))
        self.run = IndexInfoRun.from_dict(kwargs.pop('run', {}))
        super().__init__(**kwargs)