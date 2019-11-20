from typing import Dict

from loguru import logger

from cihpc.config.configure import configure_recursive, Missing
from cihpc.shared.db.mongo_db import Mongo
from cihpc.shared.db.timer_index import TimerIndex
from cihpc.shared.db.cols.col_index_info import ColIndexInfo

_default_job_index = dict(
    project='< name >',
    job='< job.name >',
    mesh='< mesh >',
    test='< test >',
    benchmark='< benchmark >',
    cpus='< cpus >',
    commit='< git.commit >',
)


def get_index(job, context: Dict) -> TimerIndex:
    """
    :type job: cihpc.config.types.project_config_job.ProjectConfigJob
    """
    extra = job.collect.extra.copy() if job.collect else _default_job_index.copy()
    extra = {k: v for k, v in extra.items() if k in _default_job_index}

    return TimerIndex(**configure_recursive(extra, context, Missing.NONE))


def create_index_info(index: TimerIndex, job) -> ColIndexInfo:
    """
    :type job: cihpc.config.types.project_config_job.ProjectConfigJob
    """
    return ColIndexInfo(
        index=index,
        run=dict(
            returncode=job.returncode,
            duration=job.duration,
        )
    )


def save_index_info(job, context: Dict):
    """
    :type job: cihpc.config.types.project_config_job.ProjectConfigJob
    """
    index = get_index(job, context)
    index_info = create_index_info(index, job)

    try:
        Mongo().col_index_info.insert(index_info)
    except Exception as e:
        logger.error(f"Could not save info to db: {e}")

def get_index_info(job, context):
    index = get_index(job, context)
    try:
        Mongo().col_index_info.find()
    except Exception as e:
        logger.error(f"Could not save info to db: {e}")