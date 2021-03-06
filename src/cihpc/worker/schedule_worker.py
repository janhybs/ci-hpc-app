import sys
MIN_PYTHON = 3, 6

if sys.version_info < MIN_PYTHON:
    sys.exit("Error: Python %s.%s or later is required.\n" % MIN_PYTHON)


from loguru import logger

from cihpc.config import get_project_config
from cihpc.parsers.main import parse_scheduler_args
from cihpc.shared.db.cols.col_schedule import ColScheduleStatus
from cihpc.shared.db.mongo_db import Mongo
from cihpc.shared.db.timer_index import TimerIndex
from cihpc.shared.g import G
from cihpc.shared.utils import data_util


ASCENDING = 1
"""Ascending sort order."""
DESCENDING = -1
"""Descending sort order."""

if __name__ == '__main__':
    args = parse_scheduler_args()

    # read yaml
    G.init(args)
    logger.info(f"Using workdir: {G.project_work_dir}")

    project_config = get_project_config(args)
    Mongo.set_default_project(project_config.name)

    cursor = Mongo().col_scheduler.find(TimerIndex(
        project=project_config.name,
        status=ColScheduleStatus.NotProcessed,
    ), alter_cursor=lambda x: x.sort("_id", DESCENDING))

    scheduler_items = list(cursor)
    total = len(scheduler_items)

    for i, schedule in enumerate(scheduler_items):
        logger.info(f"Schedule {i+1:d}/{total:2d} starting")
        _id = schedule.id
        index = schedule.index
        repetitions = schedule.details.repetitions
        project, job_name, commit, branch = data_util.pop(index, "project", "job", "commit", "branch")
        variables = {k: data_util.ensure_list(v) for k, v in data_util.valid(index.copy()).items()}

        variable_list = list()
        for k, v in variables.items():
            variable_list.append({k: v})

        project_config.set_desired_head(commit, "master")
        job = project_config.get(job_name)

        job.variables.repetitions = repetitions
        project_config.set_desired_variables(job_name, variable_list)
        project_config.initialize(with_git=False)

        print(f"{Mongo().col_scheduler.update(schedule, status=ColScheduleStatus.Running)}")

        try:
            project_config.execute()
            print(f"{Mongo().col_scheduler.update(schedule, status=ColScheduleStatus.Processed)}")
        except Exception as e:
            print(f"{Mongo().col_scheduler.update(schedule, status=ColScheduleStatus.NotProcessed)}")
            logger.error(f"Error: {e}")
