from pathlib import Path

from loguru import logger

from cihpc.config import get_project_config
from cihpc.parsers.main import parse_worker_args
from cihpc.shared.db.mongo_db import Mongo
from cihpc.shared.g import G


def test():
    _current_dir = Path(__file__).absolute().parent
    args = parse_worker_args([
        "--cfg", str(_current_dir),
        "--vars", str(_current_dir) + "/user/desired_variables.yaml",
        "--rnd=true"
    ])

    # force commit
    args.commit = "e88a8335648b08843aa58062c2488120c458d737"

    args.commit = "ec5aa26c2c53802e4f5c1d73c0baa1b756640715"

    args.commit = "25bf49f2c16f5cc3d167c5022398942dc2371c4d"

    args.commit = "61dd0ec01b450342a1eb2037a63f6f47d3071f65"

    # read yaml
    G.init(args)
    logger.info(f"Using workdir: {G.project_work_dir}")
    config = get_project_config(args)
    Mongo.set_default_project(config.name)

    config.execute()


if __name__ == '__main__':
    test()
