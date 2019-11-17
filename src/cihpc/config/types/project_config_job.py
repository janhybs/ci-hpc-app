from typing import Dict

from loguru import logger

from cihpc.config.types.job_base import JobBase
from cihpc.config.types.project_config_cache import ProjectConfigCache
from cihpc.config.types.project_config_collect import ProjectConfigCollect
from cihpc.config.types.project_config_variables import ProjectConfigVariables
from cihpc.shared.g import G

from cihpc.shared.utils import job_util


class ProjectConfigJob(JobBase):
    def __init__(self, data: Dict, project_config, index: int = 0):
        """
        :type project_config: cihpc.config.ProjectConfig
        """
        super().__init__(data, project_config, index)

        self.variables = ProjectConfigVariables(data.get('variables', []))
        self.cache = ProjectConfigCache(data.get("cache"))
        self.collect = ProjectConfigCollect(data.get("collect"))
        self.retries: int = data.get("retry") or data.get("retries") or G.BROKEN_COUNT_LIMIT

    def execute(self, context: Dict):
        logger.info(f"executing job {self.fullname}")

        context = (context or dict()).copy()
        context.update(dict(
            job=self
        ))

        if not self.if_self(context):
            logger.info(f"skipping, condition '{self.if_self_condition}' evaluated to False")
            return False

        if self.script:
            # look for the cached solution
            if self.cache:
                if self.cache.execute(context):
                    return True

            # process script if no cache hit
            self._run_script(context)

    def _handle_process_over(self, context: Dict):
        super()._handle_process_over(context)

        # no matter what, we save info that this process has finished
        job_util.save_index_info(self, context)

    def _handle_process_error(self, context: Dict):
        super()._handle_process_error(context)

    def _handle_run_success(self, context: Dict):
        super()._handle_run_success(context)

        # save cache on success
        if self.cache:
            self.cache.try_save()

        if self.collect:
            timers = list(self.collect.execute(context))
            logger.info(f"Found {len(timers)} timers")

    def expand(self, context: Dict):
        if len(self.variables) > 1:
            logger.info(f"Expanding job {self} to {len(self.variables)} jobs")

        for variation in self.variables.loop():
            new_data = self.data.copy()
            new_data.update(dict(
                _variation=f"{variation['index']:02d}",
                variables=[]
            ))

            job = ProjectConfigJob(new_data, self.project_config, self.index)
            job.construct({**context, **variation})
            yield job, context, variation
