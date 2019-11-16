from pathlib import Path
from typing import Dict
import re

from cihpc.config import _extensions
from cihpc.config._cfg import _read_yaml
from cihpc.config.project_config import ProjectConfig

cfg = None


def read_cfg(path: Path):
    _extensions.extend()
    global cfg

    result = _read_yaml(path)
    cfg = ProjectConfig(result)
    return cfg
