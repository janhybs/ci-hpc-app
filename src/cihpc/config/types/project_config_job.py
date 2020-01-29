from typing import Dict, Tuple

import cachetools
from loguru import logger

from cihpc.config.types.job_base import JobBase
from cihpc.config.types.project_config_cache import ProjectConfigCache
from cihpc.config.types.project_config_collect import ProjectConfigCollect
from cihpc.config.types.project_config_variables import ProjectConfigVariables

from cihpc.shared.g import G

from cihpc.shared.utils import job_util, data_util
from cihpc.shared.utils.data_util import first_valid


class ProjectConfigJob(JobBase):
    def __init__(self, data: Dict, project_config, index: int = 0):
        """
        :type project_config: cihpc.config.ProjectConfig
        """
        super().__init__(data, project_config, index)

        self.repetitions = first_valid(data, "repetitions", "reps", default=1)
        self.variables = ProjectConfigVariables(data.get('variables', []), self.repetitions)
        self.cache = ProjectConfigCache(data.get("cache"))
        self.collect = ProjectConfigCollect(data.get("collect"))
        self.retries: int = data.get("retry") or data.get("retries") or G.BROKEN_COUNT_LIMIT

    @property
    def default_index(self) -> Dict:
        try:
            from cihpc.shared.db.timer_index import TimerIndex
            index = TimerIndex(**job_util.get_index(
                self,
                {'job': self, **self.project_config.context}
            ))
            index["branch"] = None
            return index
        except:
            return dict()

    @property
    def pretty_index(self) -> str:
        import json
        return json.dumps(data_util.valid(self.default_index))

    @property
    @cachetools.cached(cache=cachetools.TTLCache(512, 10))
    def db_run_count(self) -> Tuple[int, int]:
        try:
            from cihpc.shared.db.db_stats import DBStats
            from cihpc.shared.db.timer_index import TimerIndex
            # print(f"loading {self.name} {self.project_config.git.main_repo.commit}")
            ok_count, broken_count = DBStats.get_run_count(self.default_index)
        except Exception as e:
            logger.warning(f"Failed to get run info for the job {self}: {e}")
            ok_count, broken_count = 0, 0

        return ok_count, broken_count

    def db_broken_count(self):
        return self.db_run_count[1]

    def db_ok_count(self):
        return self.db_run_count[0]

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
            logger.debug(f"Expanding job to {len(self.variables)} jobs: {self.pretty_index}")

        for variation in self.variables.loop():
            new_data = self.data.copy()
            new_data.update(dict(
                _variation=f"{variation['index']:02d}",
                variables=[]
            ))

            job = ProjectConfigJob(new_data, self.project_config, self.index)
            job.construct({**context, **variation})
            yield job, context, variation

    def __hash__(self):
        try:
            value = hash(f"{self.name}-{self.project_config.git.main_repo.commit}")
            return value
        except:
            return super().__hash__(self)

