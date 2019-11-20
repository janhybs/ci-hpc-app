from loguru import logger

from cihpc.config import get_project_config
from cihpc.parsers.main import parse_scheduler_args
from cihpc.repo.repo_util import RepoUtil
from cihpc.shared.db.mongo_db import Mongo
from cihpc.shared.g import G

if __name__ == '__main__':
    args = parse_scheduler_args()

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
    print(repo)
