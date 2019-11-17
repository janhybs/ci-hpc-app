from pathlib import Path

from cihpc.config import _extensions
from cihpc.config._cfg import _read_yaml
from cihpc.config.types.project_config import ProjectConfig
from cihpc.parsers.worker_parser import WorkerParser

cfg = None


def get_project_config(args: WorkerParser):
    _extensions.extend()
    global cfg

    result = _read_yaml(args.config_file)
    cfg = ProjectConfig(result, args)
    return cfg
