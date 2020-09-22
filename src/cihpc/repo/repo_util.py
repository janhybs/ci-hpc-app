from collections import defaultdict
from pathlib import Path
from typing import List, Union, Iterable, Dict

import maya
from loguru import logger
import os

from cihpc.config.types.project_config import ProjectConfig
from cihpc.config.types.project_config_git import GitSpec
from cihpc.config.types.project_config_job import ProjectConfigJob
from cihpc.shared.db.cols.col_repo_info import ColRepoInfo
from cihpc.shared.db.cols.col_schedule import ColScheduleDetails, ColSchedule, ColScheduleStatus
from cihpc.shared.db.db_stats import DBStats
from cihpc.shared.db.mongo_db import Mongo, in_list
from cihpc.shared.db.timer_index import TimerIndex
from cihpc.shared.errors.custom_errors import ProjectError
from cihpc.shared.utils import job_util, string_util
from cihpc.shared.utils.data_util import distinct
from cihpc.shared.utils.git_utils import get_active_branches, BranchCommit, extract_date_from_head, iter_revision
from git import Repo, RemoteReference, Head, Commit

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

    def _get_commits(self, branches: List[Union[str, Head]] = None, min_age=default_min_age, max_per_branch=10):
        if not branches:
            branches = get_active_branches(self.repo, min_age)

        for branch in branches:
            for commit in iter_revision(self.repo, branch.head, limit=max_per_branch):
                yield BranchCommit(branch=branch, commit=commit)

    def get_commits(self, branches: List[Union[str, Head]] = None, min_age=default_min_age, max_per_branch=10) -> \
            Iterable[BranchCommit]:
        for branch_commit in distinct(self._get_commits(branches, min_age, max_per_branch)):
            yield branch_commit

    def schedule_run(self, commit: str, branch: str, job_name: str = "test"):
        self.project_config.git.main_repo.set_fake_head(
            commit=commit,
            branch=branch
        )

        context = dict(**self.project_config.context)

        init_job = self.project_config.jobs[0]

        if init_job.db_broken_count() >= init_job.retries:
            logger.warning(f"Skipping job '{init_job}' since it already has {init_job.db_broken_count()} broken builds")
            yield 0
        else:
            test_job = self.project_config.get(job_name)
            for schedule_document, schedule_index in self._process_job(test_job, context):
                scheduled_already = DBStats.get_schedule_repetitions(schedule_index)
                schedule_document.details.repetitions -= scheduled_already
                if schedule_document.details.repetitions > 0:
                    Mongo().col_scheduler.insert(schedule_document)
                    logger.debug(
                        f"Inserted {schedule_document.details.repetitions} requests for the job:\n{test_job.pretty_index}")
                    yield schedule_document.details.repetitions
                else:
                    logger.debug(
                        f"Already scheduled {scheduled_already} runs, which is more than enough:\n{test_job.pretty_index}")

    def schedule_runs(self, branches=None, job_name: str = "test", max_per_branch=10):
        for branch_commit in self.get_commits(branches, max_per_branch=max_per_branch):
            runs = self.schedule_run(
                str(branch_commit.commit),
                branch_commit.branch.head.remote_head,
                job_name,
            )
            total = sum(runs)
            logger.info(f"Scheduled {total} requests for the commit {branch_commit.commit}")

    @classmethod
    def _process_job(cls, job: ProjectConfigJob, context: Dict):
        for sub_job, extra_context, variation in job.expand(context):
            rest = dict(job=sub_job)
            new_context = {**extra_context, **variation, **rest}
            schedule_index = TimerIndex(**job_util.get_index(job, new_context))
            ok_count, broken_count = DBStats.get_run_count(schedule_index)

            # TODO specify repetitions
            schedule_details = ColScheduleDetails(priority=0, repetitions=7)
            schedule_document = ColSchedule(
                index=schedule_index,
                details=schedule_details,
                status=ColScheduleStatus.NotProcessed,
                worker=None
            )
            yield schedule_document, schedule_index

    def to_latest(self):
        logger.info("pulling latest changes")
        self.repo.remote().pull()

    def _update_edges(self, documents: List[ColRepoInfo]):
        children = defaultdict(list)
        for d in documents:
            for p in d.parents:
                children[p].append(d.commit)

        for d in documents:
            d.children = children[d.commit]

        return documents

    def extract_info(self, per_branch, max_age, single_branch=None):
        logger.info("obtaining commit details")
        branches = single_branch if single_branch else get_active_branches(self.repo, max_age)

        info: Dict[Commit, List[str]] = defaultdict(list)
        documents = list()

        for branch in branches:
            branch_head = None if isinstance(branch, str) else branch.head
            branch_name = branch if not branch_head else str(branch.head)
            branch_full = f"origin/{branch_name}" if not branch_name.startswith("origin/") else branch_name
            branch_short = branch_full[7:]

            for commit in iter_revision(self.repo, branch_head or branch_full, limit=per_branch, first_parent=False):
                info[commit].append(branch_short)

        for commit, branches in info.items():
            doc = ColRepoInfo()
            doc.author = commit.author.name
            doc.email = commit.author.email
            doc.commit = commit.hexsha
            doc.branches = branches
            doc.branch = None if len(branches) > 1 else branches[0]
            doc.authored_datetime = commit.authored_datetime
            doc.committed_datetime = commit.committed_datetime
            doc.message = commit.message
            doc.distance = -1
            doc.parents = [c.hexsha for c in commit.parents]
            documents.append(doc)

        logger.info("comparing changes in db")
        # to_be_updated = [doc.commit for doc in documents]
        # rexisting_cmts = [x.commit for x in Mongo().col_repo_info.find({}, {"commit": 1})]
        results = Mongo().col_repo_info.find(
            {"commit": in_list([doc.commit for doc in documents])},
            ["commit"],
            raw=True
        )

        logger.info("traversing parents")
        documents = self._update_edges(documents)

        existing = [r.commit for r in results]
        filtered = [d for d in documents if d.commit not in existing]
        logger.info(f"inspected total of {len(documents)} commits, {len(filtered)} new ones")

        if filtered:
            Mongo().col_repo_info.insert_many(filtered)
        else:
            logger.info(f"no new commits to add...")

        logger.info("updating commit parents and children")
        changes = list(Mongo().col_repo_info.batch_update(
            documents,
            lambda x: dict(commit=x.commit),
            lambda x: dict(
                parents=x.parents,
                children=x.children
            ),
        ))
        logger.info(f"updated {len(changes)} parents and children")
