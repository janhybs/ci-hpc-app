#!/bin/python3
# author: Jan Hybs
from typing import Optional
from cihpc.shared.db.models import Entity


class TimerIndex(Entity):
    project: Optional[str]
    commit: Optional[str]
    branch: Optional[str]

    job: Optional[str]
    test: Optional[str]
    benchmark: Optional[str]
    mesh: Optional[str]
    cpus: Optional[int]

    frame: Optional[str]
    uuid: Optional[str]

    host: Optional[str]

    mesh_cpus: Optional[int]
    mesh_size: Optional[int]

    def __init__(self, **kwargs):
        self.project = None
        self.commit = None
        self.branch = None

        self.job = None
        self.test = None
        self.benchmark = None
        self.mesh = None
        self.cpus = None

        self.frame = None
        self.uuid = None

        self.host = None

        self.mesh_cpus = None
        self.mesh_size = None
        super().__init__(**kwargs)
