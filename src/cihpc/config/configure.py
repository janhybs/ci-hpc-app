import enum
import re
import sys
import os
import platform
from pathlib import Path
from typing import Dict, Match, Union, Iterable

from cihpc.shared.errors.config_error import ConfigError
from cihpc.shared.g import G

_configure_object_regex = re.compile(r'<([a-zA-Z0-9_ .()\[\]{\}\-+*/\'"]+)>')
_hostname = platform.node()


class Missing(enum.Enum):
    KEEP_ORIGINAL = 1
    RAISE_ERROR = 2
    NONE = 3


class _EnvGetter:
    def __getattr__(self, item):
        return os.environ.get(item)

    def __getitem__(self, item):
        return os.environ.get(item)


def get_output(cmd: str) -> str:
    import subprocess
    return subprocess.getoutput(cmd)


_global_context = dict(
    sys=sys,
    Path=Path,
    env=_EnvGetter(),
    workdir=lambda: G.project_work_dir,
    cwd=lambda: os.getcwd(),
    get_output=get_output,
    hostname=_hostname
)


def configure(template: str, context: Dict=None, keep_missing: Missing = Missing.KEEP_ORIGINAL):
    if not template:
        return template

    context = context or {}

    def _replace(match: Match) -> str:
        subject = match.group(1)
        try:
            return str(eval(subject, context, _global_context))
        except NameError:
            if keep_missing is Missing.KEEP_ORIGINAL:
                return match.group(0)
            elif keep_missing is Missing.NONE:
                return 'null'
            else:
                raise

    template = str(template)

    if template.startswith("<<") and template.endswith(">>"):
        try:
            return eval(template[2:-2], context, _global_context)
        except NameError:
            if keep_missing:
                return template
            raise

    if template.startswith("<") and template.endswith(">") and template.count("<") == template.count(">") == 1:
        try:
            return eval(template[1:-1], context, _global_context)
        except NameError:
            if keep_missing is Missing.KEEP_ORIGINAL:
                return template
            elif keep_missing is Missing.NONE:
                return None
            else:
                raise

    return _configure_object_regex.sub(_replace, str(template))


def configure_recursive(o: Union[Iterable, Dict, str], context: Dict=None, keep_missing: Missing = Missing.KEEP_ORIGINAL):
    if not o:
        return o

    if isinstance(o, str):
        return configure(o, context, keep_missing)

    if isinstance(o, Dict):
        return {key: configure_recursive(value, context, keep_missing) for key, value in o.items()}

    if isinstance(o, Iterable):
        return [configure_recursive(value, context, keep_missing) for value in o]

    return o
