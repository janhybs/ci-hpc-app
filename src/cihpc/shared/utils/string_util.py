import os
import random
from pathlib import Path
from uuid import uuid4
from typing import List, Union


def rand_str(length: int=16):
    return ''.join(random.choice('0123456789abcdef') for _ in range(length))


def uuid():
    return str(uuid4())


def generate_bash(path: Path, content: Union[List[str]]):
    lines = ["#!/bin/bash"] + content

    path.write_text('\n\n'.join(lines))
    os.chmod(str(path), 0o777)
