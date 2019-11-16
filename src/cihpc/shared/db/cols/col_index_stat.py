#!/bin/python3
# author: Jan Hybs

from itertools import groupby
from typing import List, Dict, Optional

from cihpc.shared.db.timer_index import TimerIndex
from cihpc.shared.db.models import (
    Entity,
    IdEntity,
)


class ColIndexStatComputed(Entity):
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


class ColIndexStat(IdEntity):
    index: TimerIndex

    stat: ColIndexStatComputed

    def __init__(self, **kwargs):
        self.index = TimerIndex.from_dict(kwargs.pop('index', {}))
        self.stat = ColIndexStatComputed.from_dict(kwargs.pop('stat', {}))
        super().__init__(**kwargs)