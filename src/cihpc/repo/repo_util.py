from pathlib import Path
from typing import List, Union, Iterable

import maya
from loguru import logger
import os

from cihpc.config.types.project_config import ProjectConfig
from cihpc.config.types.project_config_git import GitSpec
from cihpc.shared.db.cols.col_schedule import ColScheduleDetails, ColSchedule
from cihpc.shared.db.db_stats import DBStats
from cihpc.shared.db.timer_index import TimerIndex
from cihpc.shared.utils import job_util, string_util
from cihpc.shared.utils.data_util import distinct
from cihpc.shared.utils.git_utils import get_active_branches, BranchCommit, extract_date_from_head, iter_revision
from git import Repo, RemoteReference, Head


default_min_age = maya.when('6 months ago')


class RepoUtil:
    def __init__(self, dir: Path, url: str, project_config: ProjectConfig = None):
        self.url = url
        self.name = str(os.path.basename(url).split('.')[0])
        self.dir = dir / self.name
        self.project_config = project_config

        if self.dir.exists():
            logger.info(f"Reading repo from {self.dir}")
            self.repo = Repo(str(self.dir))
        else:
            logger.info(f"Cloning repo from {self.url}")
            self.dir.parent.mkdir(parents=True, exist_ok=True)
            self.repo = Repo.clone_from(
                self.url,
                str(self.dir),
            )

        self.schedule_runs()

    def _get_commits(self, branches: List[Union[str, Head]] = None, min_age=default_min_age, max_per_branch=10):
        if not branches:
            branches = get_active_branches(self.repo, min_age)

        for branch in branches:
            for commit in iter_revision(self.repo, branch.head, limit=max_per_branch):
                yield BranchCommit(branch=branch, commit=commit)

    def get_commits(self, branches: List[Union[str, Head]] = None, min_age=default_min_age, max_per_branch=10) -> Iterable[BranchCommit]:
        for branch_commit in distinct(self._get_commits(branches, min_age, max_per_branch)):
            yield branch_commit

    def schedule_run(self, commit: str, branch: str, job_name: str = "test"):

        self.project_config.git.main_repo.set_fake_head(
            commit=commit,
            branch=branch
        )

        context = dict(**self.project_config.context)
        job = self.project_config.get(job_name)

        for sub_job, extra_context, variation in job.expand(context):
            rest = dict(job=sub_job)
            new_context = {**extra_context, **variation, **rest}
            schedule_index = TimerIndex(**job_util.get_index(job, new_context))
            # TODO specify repetitions
            schedule_details = ColScheduleDetails(priority=0, repetitions=7)
            schedule_document = ColSchedule(index=schedule_index, details=schedule_details)

            print(DBStats.get_run_count(schedule_index))

    def schedule_runs(self, branches=None, job_name: str = "test"):
        for branch_commit in self.get_commits(branches):
            self.schedule_run(
                str(branch_commit.commit),
                branch_commit.branch.head.remote_head,
                job_name,
            )
