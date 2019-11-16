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

    def __init__(self, **kwargs):
        self.timestamp = float(kwargs.pop('timestamp', time.time()))
        self.is_broken = None
        super().__init__(**kwargs)


class IndexInfoStat(Entity):
    pval: Optional[float]
    stat: Optional[float]
    a: Optional[List[str]]
    b: Optional[List[str]]

    def __init__(self, **kwargs):
        self.pval = None
        self.stat = None
        self.a = kwargs.pop('a', [])
        self.b = kwargs.pop('b', [])
        super().__init__(**kwargs)

    @staticmethod
    def _reduced(lst: List[str]) -> Dict[str, int]:
        return {k: len(list(v)) for k, v in groupby(sorted(lst or []))}

    @property
    def sample_size(self):
        return len(self.a) + len(self.b)

    @property
    def reduced_a(self) -> Dict[str, int]:
        return self._reduced(self.a)

    @property
    def reduced_b(self) -> Dict[str, int]:
        return self._reduced(self.b)


class ColIndexInfo(IdEntity):
    index: TimerIndex
    runs: List[IndexInfoRun]

    stat: IndexInfoStat
    stats: List[IndexInfoStat]

    def __init__(self, **kwargs):
        self.index = TimerIndex.from_dict(kwargs.pop('index', {}))
        self.runs = [IndexInfoRun.from_dict(x) for x in kwargs.pop('runs', [])]

        self.stat = IndexInfoStat.from_dict(kwargs.pop('stat', {}))
        self.stats = [IndexInfoStat.from_dict(x) for x in kwargs.pop('stats', [])]
        super().__init__(**kwargs)

    @property
    def run_count(self):
        return len(self.runs)

    @property
    def broken_runs(self):
        return [x for x in self.runs if x.is_broken]

    @property
    def broken_count(self):
        return len(self.broken_runs)

    @staticmethod
    def find_same_index():
        pass
