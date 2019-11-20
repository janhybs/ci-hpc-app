#!/bin/python3
# author: Jan Hybs
from typing import Optional

from cihpc.shared.db.timer_index import TimerIndex
from cihpc.shared.db.models import (
    Entity,
    IdEntity,
)


class ColScheduleDetails(Entity):
    priority: Optional[float]
    repetitions: Optional[int]

    def __init__(self, **kwargs):
        self.priority = kwargs.pop("priority", None)
        self.repetitions = kwargs.pop("repetitions", None)
        super().__init__(**kwargs)


class ColSchedule(IdEntity):
    index: TimerIndex
    details: ColScheduleDetails
    status: Optional[str]

    def __init__(self, **kwargs):
        self.index = TimerIndex.from_dict(kwargs.pop('index', {}))
        self.details = ColScheduleDetails.from_dict(kwargs.pop('details', {}))
        self.status = kwargs.pop("status", None)
        super().__init__(**kwargs)
