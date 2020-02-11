from pathlib import Path
from typing import Dict, List

from tap import Tap

from cihpc.shared.errors.config_error import ConfigError
from cihpc.shared.utils.io_util import read_json, read_yaml


class CommonParser(Tap):
    config_file: Path
    commit: str = None
    branch: str = "master"
    random_workdir: str = ""
    variable_file: Dict[str, List] = dict()
    sections: List[str] = list()

    @staticmethod
    def _get_config_path(value) -> Path:
        path = Path(value)

        if not path.exists():
            raise ConfigError("file does not exists")

        if path.is_file():
            return path

        return path / 'config.yaml'

    @property
    def config_dir(self) -> Path:
        return self.config_file.parent

    @staticmethod
    def _parse_variables(value: str) -> Dict[str, List]:
        if value:
            if value.endswith(".json"):
                return read_json(value)
            return read_yaml(value)
        return dict()

    def add_arguments(self):
        self.add_argument("-c", "--config-file", "--config", "--cfg", type=self._get_config_path)
        self.add_argument("--random-workdir", "--rnd")
        self.add_argument("--variable-file", "--var", "--vars", type=self._parse_variables)
        self.add_argument("sections", nargs="*", type=str)
