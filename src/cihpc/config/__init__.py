from pathlib import Path

from cihpc.config import _extensions
from cihpc.config._cfg import _read_yaml
from cihpc.config.types.project_config import ProjectConfig
from cihpc.parsers.common_parser import CommonParser


def get_project_config(args: CommonParser):
    _extensions.extend()

    result = _read_yaml(args.config_file)
    return ProjectConfig(result, args)
