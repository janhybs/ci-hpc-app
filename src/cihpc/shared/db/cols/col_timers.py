#!/bin/python3
# author: Jan Hybs
from typing import Optional
from cihpc.shared.db.timer_index import TimerIndex
from cihpc.shared.db.models import (
    Entity,
    IdEntity,
)


class ColTimerSystem(Entity):
    hostname: Optional[str]
    username: Optional[str]
    name: Optional[str]

    os_version: Optional[str]
    os_name: Optional[str]

    def __init__(self, **kwargs):
        self.hostname = None
        self.username = None
        self.name = None

        self.os_version = None
        self.os_name = None
        super().__init__(**kwargs)


class ColTimerProblem(Entity):
    task_size: Optional[int]
    cpus: Optional[float]

    def __init__(self, **kwargs):
        self.task_size = None
        self.cpus = None
        super().__init__(**kwargs)


class ColTimerResult(Entity):
    duration: Optional[float]
    executed: Optional[float]
    cnt_alloc: Optional[float]
    cnt_dealloc: Optional[float]
    mem_alloc: Optional[float]
    mem_dealloc: Optional[float]
    file_path: Optional[str]
    function: Optional[str]
    name: Optional[str]
    file_line: Optional[int]
    dur_ratio: Optional[float]
    path: Optional[str]

    def __init__(self, **kwargs):
        self.duration = None
        self.executed = None
        self.cnt_alloc = None
        self.cnt_dealloc = None
        self.mem_alloc = None
        self.mem_dealloc = None
        self.file_path = None
        self.function = None
        self.name = None
        self.file_line = None
        self.dur_ratio = None
        self.path = None
        super().__init__(**kwargs)


class ColTimer(IdEntity):
    index: TimerIndex
    system: ColTimerSystem
    problem: ColTimerProblem
    result: ColTimerResult

    def __init__(self, **kwargs):
        self.index = TimerIndex.from_dict(kwargs.pop('index', {}))
        self.system = ColTimerSystem.from_dict(kwargs.pop('system', {}))
        self.problem = ColTimerProblem.from_dict(kwargs.pop('problem', {}))
        self.result = ColTimerResult.from_dict(kwargs.pop('result', {}))
        super().__init__(**kwargs)
