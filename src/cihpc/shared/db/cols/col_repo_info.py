#!/bin/python3
# author: Jan Hybs

from typing import List, Dict, Optional

import datetime
from cihpc.shared.db.timer_index import TimerIndex
from cihpc.shared.db.models import (
    Entity,
    IdEntity,
)


class ColRepoInfo(IdEntity):
    author: str
    email: str
    commit: str
    branch: str
    message: str
    distance: int
    authored_datetime: datetime.datetime
    committed_datetime: datetime.datetime

    # list of candidates
    branches: List[str]

    def __init__(self, **kwargs):
        self.branches = kwargs.pop('branches', [])
        super().__init__(**kwargs)