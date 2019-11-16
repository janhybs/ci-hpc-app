from pathlib import Path

from cihpc.config import read_cfg
from cihpc.parsers.main import parse_worker_args
from cihpc.shared.db.mongo_db import Mongo
from cihpc.shared.g import G


__dir__ = Path(__file__).parent.absolute()


def test():
    args = parse_worker_args(["--cfg", str(__dir__)])

    # read yaml
    G.init(args)
    config = read_cfg(args.config_file)
    Mongo.set_default_project(config.name)

    config.execute()
