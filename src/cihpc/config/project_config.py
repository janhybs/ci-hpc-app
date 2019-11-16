from pathlib import Path
from typing import Dict, List
import os

from loguru import logger

from cihpc.config.configure import configure
from cihpc.config.types.project_config_git import ProjectConfigGit
from cihpc.config.types.project_config_job import ProjectConfigJob
from cihpc.shared.errors.job_error import JobError
from cihpc.shared.utils import string_util
from cihpc.shared.utils.data_util import first_valid


class ProjectConfig:
    def __init__(self, data: Dict):
        self.name: str = data["name"]

        self.workdir: Path = Path(configure(data.get("workdir", f'<workdir()>/{self.name}')))
        self.tmpdir: Path = Path(configure(data.get("tmpdir", f'<workdir()>/{self.name}/.tmp')))

        self.before_run: str = first_valid(data, "init-shell", "before-run")
        self.after_run: str = first_valid(data, "after-shell", "after-run")

        self.git = ProjectConfigGit(data["git"])
        self.context = dict(
            name=self.name,
            workdir=self.workdir,
            tmpdir=self.tmpdir,
        )

        self.jobs: List[ProjectConfigJob] = list()
        for index, job in enumerate(first_valid(data, "steps", "pipeline") or []):
            self.jobs.append(ProjectConfigJob(job, self, index))

    def __repr__(self):
        return f"<ProjectConfig({self.workdir})>"

    def execute(self, context=None):
        self.workdir.mkdir(parents=True, exist_ok=True)
        os.chdir(str(self.workdir))
        context = {**self.context, **(context or {})}

        if self.git.main_repo:
            logger.info(f"Setting up main repository {self.git.main_repo.name}")
            # TODO: set branch/commit
            self.git.main_repo.initialize()
            context.update(
                dict(git=self.git.main_repo)
            )

        for repo_name, repo in self.git.deps.items():
            if repo:
                logger.info(f"Setting up secondary repository {repo.name}")
                repo.initialize()

        for job in self.jobs:
            for sub_job, extra_context, variation in job.expand(context):
                rest = dict(uuid=string_util.uuid())
                new_context = {**extra_context, **variation, **rest}
                sub_job.construct(new_context)

                try:
                    sub_job.execute(new_context)
                except JobError as e:
                    logger.error("JobError: terminating workflow...")
