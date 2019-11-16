import yaml
from typing import List, Dict
from pathlib import Path


def _read_yaml(path: Path) -> Dict:
    return yaml.safe_load(path.read_text())