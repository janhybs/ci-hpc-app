from pathlib import Path
from tap import Tap

from cihpc.shared.errors.config_error import ConfigError


class CommonParser(Tap):
    config_file: Path
    random_workdir: str = ""

    def _get_config_path(self, value) -> Path:
        path = Path(value)

        if not path.exists():
            raise ConfigError("file does not exists")

        if path.is_file():
            return path

        return path / 'config.yaml'

    @property
    def config_dir(self) -> Path:
        return self.config_file.parent

    def add_arguments(self):
        self.add_argument("-c", "--config-file", "--config", "--cfg", type=self._get_config_path)
        self.add_argument("--random-workdir", "--rnd")
