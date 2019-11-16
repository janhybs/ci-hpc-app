import os
import subprocess
from pathlib import Path
from typing import Dict, Optional
from loguru import logger

from cihpc.config.configure import configure
from cihpc.config.types.project_config_cache import ProjectConfigCache
from cihpc.config.types.project_config_collect import ProjectConfigCollect
from cihpc.config.types.project_config_variables import ProjectConfigVariables
from cihpc.shared.errors.job_error import JobError
from cihpc.shared.utils.data_util import first_valid
from cihpc.shared.utils.io_util import get_streamable
from cihpc.shared.utils.string_util import generate_bash


class ProjectConfigJob:
    def __init__(self, data: Dict, project_config, index: int=0):
        """
        :type project_config: cihpc.config.ProjectConfig
        """
        self.data = data
        self.index: int = index
        self.script: Optional[Path] = None
        self.project_config = project_config

        self.name: str = first_valid(data, "id", "name", "step", "job")

        self.runs: str = first_valid(data, "runs", "run")
        self.shell: str = data.get("shell", "bash")
        self.uses: str = data.get("uses")
        
        self.variables = ProjectConfigVariables(data.get('variables', []))
        self.cache = ProjectConfigCache(data.get("cache"))

        self.if_self_condition: Optional[str] = data.get("if")
        self.stdout = get_streamable(first_valid(data, "stdout", "output") or subprocess.DEVNULL)
        self.stderr = get_streamable(first_valid(data, "stderr", "error") or subprocess.STDOUT)

        self.timeout: float = data.get("timeout")
        self.collect = ProjectConfigCollect(data.get("collect"))

        self.continue_on_error: bool = data.get("continue-on-error", False)

        self.on_success: str = data.get("on-success")
        self.on_success_script: Optional[Path] = None

        self.on_failure: str = data.get("on-failure")
        self.on_failure_script: Optional[Path] = None

        self._variation: str = data.get('_variation', "")

    def if_self(self, context: Dict):
        if self.if_self_condition is None:
            return True

        result = str(configure(self.if_self_condition, context, False)).lower()
        return result in ("1", "true", "yes", "on")

    @property
    def workdir(self) -> Path:
        return self.project_config.workdir / ".cihpc" / f"{self.index:02d}-{self.name}{self._variation}"

    def __repr__(self):
        return f"<ProjectConfigJob({self.name}{self._variation})>"

    def construct(self, context: Dict):
        """
        :type context: Dict
        """
        self.workdir.mkdir(parents=True, exist_ok=True)
        # TODO: other shell types

        if self.runs:
            self.script = self.workdir / 'run.sh'
            self.runs = configure(self.runs, context)

            script_content = list()
            if self.project_config.before_run:
                script_content.append(configure(self.project_config.before_run, context))

            script_content.append(self.runs)

            if self.project_config.after_run:
                script_content.append(configure(self.project_config.after_run, context))

            generate_bash(self.script, script_content)

        if self.on_success:
            self.on_success_script = self.workdir / 'on-success.sh'
            generate_bash(self.on_success_script, [configure(self.on_success, context)])

        if self.on_failure:
            self.on_failure_script = self.workdir / 'on-failure.sh'
            generate_bash(self.on_failure_script, [configure(self.on_failure, context)])

    def execute(self, context: Dict):
        context = (context or dict()).copy()
        context.update(dict(
            job=self
        ))

        logger.info(f"executing job {self.name}")

        if self.collect:
            self.collect.execute(context)

        if not self.if_self(context):
            logger.info(f"skipping, condition '{self.if_self_condition}' evaluated to False")
            return False

        if self.script:
            # look for the cached solution
            if self.cache:
                if self.cache.execute(context):
                    return True

            # execute the script
            with self.stdout as stdout, self.stderr as stderr:
                process = subprocess.Popen(
                    ['bash', str(self.script)],
                    stdout=stdout,
                    stderr=stderr,
                )

                # save pid
                pid = process.pid

                try:
                    process.wait(self.timeout)
                except subprocess.TimeoutExpired:
                    import psutil
                    parent = psutil.Process(pid)
                    for child in parent.children(recursive=True):
                        child.kill()
                    parent.kill()
                    process.wait()
                    logger.error(f"{pid} terminated ({process.returncode})")

            # terminate on failure
            if process.returncode != 0:
                if self.continue_on_error:
                    logger.warning(f"job {self.name} failed but still continuing...")
                else:
                    raise JobError()

            # save cache on success
            if process.returncode == 0 or self.continue_on_error:
                if self.cache:
                    self.cache.try_save()

                if self.collect:
                    self.collect.execute(context)

            # run cleanup scripts
            if process.returncode != 0:
                if self.on_failure:
                    subprocess.Popen(["bash", str(self.on_failure_script)]).wait()
            else:
                if self.on_success:
                    subprocess.Popen(["bash", str(self.on_success_script)]).wait()

    def expand(self, context: Dict):
        for variation in self.variables.loop():
            new_data = self.data.copy()
            new_data.update(dict(
                _variation=f"{variation['index']:02d}",
                variables=[]
            ))

            job = ProjectConfigJob(new_data, self.project_config, self.index)
            job.construct({ **context, **variation })
            yield job, context, variation
