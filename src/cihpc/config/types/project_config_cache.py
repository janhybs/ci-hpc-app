import os
import shutil
from pathlib import Path
from typing import Dict, Optional

from loguru import logger

from cihpc.config.configure import configure, configure_recursive
from cihpc.shared.utils.timer import log_duration

_default_storage = '<env.HOME>/.cache/cihpc'


class ProjectConfigCache:
    """
    A class which handles project caching
    """

    def __init__(self, data):

        if not data:
            self.directories = None
            self.storage = None
            self.fields = None

        elif isinstance(data, dict):
            self.directories = data['directories']  # required
            self.storage = Path(data.get('storage', _default_storage))  # default is home .cache dir
            self.fields = data.get('fields', dict())

        elif isinstance(data, list):
            self.storage = Path(_default_storage)
            self.directories = data
            self.fields = dict()

        elif isinstance(data, str):
            self.enabled = True
            self.storage = Path(_default_storage)
            self.directories = [data]
            self.fields = dict()

        else:
            raise ValueError('kwargs must be dictionary, string or list')

        self.cache_folder_name = "<name>-<git.commit>"
        self.cache_dir: Optional[Path] = None
        self.was_restored = False

    @log_duration()
    def restore(self):
        for dirname in self.directories:
            from_dir = self.cache_dir / dirname
            to_dir = Path(dirname).absolute()

            if not from_dir.exists():
                continue

            logger.debug(f'restoring cache dir {dirname}')
            if os.path.exists(to_dir):
                logger.debug(f'rm tree {to_dir}')
                shutil.rmtree(to_dir)
            shutil.copytree(str(from_dir), str(to_dir))

        self.was_restored = True

    @log_duration()
    def save(self):
        for dirname in self.directories:
            from_dir = Path(dirname).absolute()
            to_dir = self.cache_dir / dirname

            if not from_dir.exists():
                continue

            logger.debug(f'saving cache dir {dirname}')
            if to_dir.exists():
                logger.debug(f'rm tree {to_dir}')
                shutil.rmtree(to_dir)
            shutil.copytree(str(from_dir), str(to_dir))

        return True

    def execute(self, context: Dict):
        self.storage = configure(self.storage, context)
        self.directories = configure_recursive(self.directories, context)
        self.cache_dir = Path(self.storage, configure(self.cache_folder_name, context))

        if self.cache_dir.exists():
            self.restore()

        return self.was_restored

    def try_save(self):
        if self.was_restored:
            return False
        return self.save()

    def __bool__(self):
        return bool(self.directories)
