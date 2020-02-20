import sys
MIN_PYTHON = 3, 6

if sys.version_info < MIN_PYTHON:
    sys.exit("Error: Python %s.%s or later is required.\n" % MIN_PYTHON)


from loguru import logger

from cihpc.config import get_project_config
from cihpc.parsers.main import parse_repo_info_args
from cihpc.shared.db.mongo_db import Mongo
from cihpc.shared.g import G
from cihpc.repo.repo_util import RepoUtil

if __name__ == '__main__':
    args = parse_repo_info_args()

    # read yaml
    G.init(args)
    logger.info(f"Using workdir: {G.project_work_dir}")

    project_config = get_project_config(args)
    Mongo.set_default_project(project_config.name)

    project_config.initialize(with_git=False)
    repo = RepoUtil(
        dir=G.project_work_dir / '.cihpc' / '.repo',
        url=project_config.git.main_repo.url,
        project_config=project_config
    )

    # update to latest
    repo.to_latest()

    # extract commit details
    repo.extract_info(
        args.per_branch,
        args.max_age,
        args.only
    )
