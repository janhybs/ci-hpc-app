import os
import sys
import pathlib
from typing import Dict, Optional

__root__ = str(pathlib.Path(__file__).parent.parent.parent.parent)
__cfg__ = os.path.join(__root__, 'cfg')

__cwd__ = os.getcwd()
__home__ = os.environ.get('CIHPC_HOME', None) or os.environ.get('CIHPC_ROOT', None) or __cwd__
__src__ = os.path.join(__root__, 'src')
__tmp__ = os.environ.get('CIHPC_TMP') or os.path.join(__root__, '.tmp')

__main_py__ = sys.argv[0]
__secret_yaml__ = os.environ.get('CIHPC_SECRET', None) or os.path.join(__cfg__, '.secret.yaml')


class G:
    tty = getattr(sys.stdout, 'isatty', lambda: False)()
    root = __root__
    src = __src__
    cwd = __cwd__
    home = __home__
    version = '2019-2'

    # path to the main.py
    main_py = __main_py__
    exec_args = [sys.executable, __main_py__]

    # this file should be PROTECTED, as it may contain passwords and database connection details
    cfg_secret_path = __secret_yaml__
    _cfg_secret_yaml: Optional[Dict] = None

    project_cfg_dir: pathlib.Path = None
    project_work_dir: pathlib.Path = None

    @classmethod
    def init(cls, parser):
        """
        :type parser: cihpc.parsers.common_parser.CommonParser
        """
        from cihpc.shared.utils.string_util import uuid

        cls.project_cfg_dir = parser.config_dir

        if parser.random_workdir:
            if parser.random_workdir.lower() in ('1', 'true', 'yes'):
                cls.project_work_dir = pathlib.Path(__tmp__, uuid())
            else:
                cls.project_work_dir = pathlib.Path(__tmp__, parser.random_workdir)
        else:
            cls.project_work_dir = pathlib.Path(__tmp__)

    @classmethod
    def get_secret(cls, project_name: str) -> Dict:
        if not cls._cfg_secret_yaml:
            import yaml
            cls._cfg_secret_yaml = yaml.safe_load(pathlib.Path(cls.cfg_secret_path).read_text())

        return cls._cfg_secret_yaml.get(project_name)

