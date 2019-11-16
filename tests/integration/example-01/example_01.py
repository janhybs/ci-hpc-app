from pathlib import Path

from cihpc.config import read_cfg
from cihpc.parsers.main import parse_worker_args
from cihpc.shared.db.mongo_db import Mongo
from cihpc.shared.g import G


def test():
    _current_dir = Path(__file__).absolute().parent
    args = parse_worker_args(["--cfg", str(_current_dir)])

    # read yaml
    G.init(args)
    config = read_cfg(args.config_file)
    Mongo.set_default_project(config.name)

    config.execute()
