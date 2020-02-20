from pathlib import Path
from typing import Dict, List
import os

from loguru import logger

from cihpc.config.configure import configure
from cihpc.config.types.project_config_git import ProjectConfigGit
from cihpc.config.types.project_config_job import ProjectConfigJob
from cihpc.parsers.common_parser import CommonParser
from cihpc.shared.db.db_stats import DBStats
from cihpc.shared.errors.custom_errors import JobError, ProjectError
from cihpc.shared.g import G
from cihpc.shared.utils import string_util, job_util
from cihpc.shared.utils.data_util import first_valid


class ProjectConfig:
    def __init__(self, data: Dict, args: CommonParser):
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
            git=self.git.main_repo
        )

        self.jobs: List[ProjectConfigJob] = list()
        self.jobs_queue: List[ProjectConfigJob] = list()
        for index, job in enumerate(first_valid(data, "steps", "pipeline") or []):
            self.jobs.append(ProjectConfigJob(job, self, index))

        # args override
        self.set_desired_head(args.commit, args.branch)
        self.desired_variables: Dict[str, List] = dict()
        for job, var in args.variable_file.items():
            self.set_desired_variables(job, var)
        
        if args.sections:
            for section in args.sections:
                jobs = [j for j in self.jobs if j.name == section]
                if jobs:
                    self.jobs_queue.append(jobs[0])
                else:
                    logger.error(f"Could not find job with name '{section}'")
        else:
            self.jobs_queue = self.jobs.copy()


    def get(self, job_name:str):
        for job in self.jobs:
            if job.name == job_name:
                return job

        return None

    def __getitem__(self, item):
        return self.get(item)

    def __repr__(self):
        return f"<ProjectConfig({self.workdir})>"

    def set_desired_head(self, commit, branch):
        if self.git.main_repo:
            self.git.main_repo.set_desired_head(
                commit=commit,
                branch=branch
            )

    def set_desired_variables(self, job_name: str, variables: List):
        self.desired_variables[job_name] = variables

    def initialize(self, context=None, with_git=True):
        context = {**self.context, **(context or {})}
        self.workdir.mkdir(parents=True, exist_ok=True)
        os.chdir(str(self.workdir))

        # setup git
        if with_git:
            self._setup_git(context)

        for job in self.jobs:
            if job.name in self.desired_variables:
                job.variables.set_variables(
                    [dict(matrix=self.desired_variables[job.name])]
                )

    def execute(self, context=None):
        self.initialize(context)

        try:
            self._run_jobs(context)
        except ProjectError as e:
            logger.error(f"Error: {e}")
            # exit(1)

    def _run_jobs(self, context):
        context = {**self.context, **(context or {})}

        jobs = list(self.jobs_queue)
        jobs_total = len(jobs)

        for i, job in enumerate(jobs):
            logger.info(f"section {i+1}/{jobs_total} {job.name}")
            subjobs = list(job.expand(context))
            subjobs_total = len(subjobs)

            for j, (sub_job, extra_context, variation) in enumerate(subjobs):
                if subjobs_total > 1:
                    logger.info(f"configuration {j+1}/{subjobs_total} {sub_job}")
                
                rest = dict(uuid=string_util.uuid(), job=sub_job)
                new_context = {**extra_context, **variation, **rest}
                sub_job.construct(new_context)

                lookup_index = job_util.get_index(sub_job, new_context)
                ok_count, broken_count = DBStats.get_run_count(lookup_index)
                logger.info(f"Found {ok_count} successful and {broken_count} failed builds for the job: \n{sub_job.pretty_index}")

                if broken_count >= sub_job.retries:
                    logger.warning(f"Skipping job since it already has {broken_count} broken builds: \n{sub_job.pretty_index}")
                    if sub_job.continue_on_error:
                        continue
                    else:
                        raise ProjectError("Skipping build since broken count has reached its limit")

                try:
                    sub_job.execute(new_context)
                except JobError as e:
                    logger.error("JobError: terminating workflow...")
                    raise ProjectError(f"Terminating build since job {sub_job} failed")

            job.try_delete_after()

    def _setup_git(self, context):
        if self.git.main_repo:
            logger.info(f"Setting up main repository {self.git.main_repo.name}")
            self.git.main_repo.initialize()

        for repo_name, repo in self.git.deps.items():
            if repo:
                logger.info(f"Setting up secondary repository {repo.name}")
                repo.initialize()
