#!/bin/python3
# author: Jan Hybs

from cihpc.shared.db.timer_index import TimerIndex
from cihpc.shared.db.models import (
    Entity,
    IdEntity,
)


class ColSchedulerDetails(Entity):
    priority: float
    repetitions: int


class ColScheduler(IdEntity):
    index: TimerIndex
    details: ColSchedulerDetails

    def __init__(self, **kwargs):
        self.index = TimerIndex.from_dict(kwargs.pop('index', {}))
        self.details = ColSchedulerDetails.from_dict(kwargs.pop('details', {}))
        super().__init__(**kwargs)
