import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict

from loguru import logger

from cihpc.config.configure import configure
from cihpc.shared.errors.custom_errors import JobError
from cihpc.shared.utils.data_util import first_valid
from cihpc.shared.utils.io_util import get_streamable
from cihpc.shared.utils.string_util import generate_bash
from cihpc.worker.plugins.progress_report import ProgressReport


class JobBase:
    def __init__(self, data: Dict, project_config, index: int = 0):
        """
        :type project_config: cihpc.config.ProjectConfig
        """
        self.data = data
        self.project_config = project_config
        self.index: int = index

        self.runs: str = first_valid(data, "runs", "run")
        self.shell: str = data.get("shell", "bash")

        self._process: Optional[subprocess.Popen] = None
        self.script: Optional[Path] = None
        self._starttime, self._endtime = 0, 0

        self.timeout: float = data.get("timeout")

        self._variation: str = data.get('_variation', "")
        self.name: str = first_valid(data, "id", "name", "step", "job")

        self.stdout = get_streamable(first_valid(data, "stdout", "output", default="devnull"))
        self.stderr = get_streamable(first_valid(data, "stderr", "error", default="stdout"))

        self.on_success: str = data.get("on-success")
        self.on_success_script: Optional[Path] = None

        self.on_failure: str = data.get("on-failure")
        self.on_failure_script: Optional[Path] = None

        self.if_self_condition: Optional[str] = data.get("if")

        self.continue_on_error: bool = data.get("continue-on-error", False)
        self.delete_after: bool = first_valid(data, "delete-after", "clean-after") or False

    def if_self(self, context: Dict):
        if self.if_self_condition is None:
            return True

        result = str(configure(self.if_self_condition, context)).lower()
        return result in ("1", "true", "yes", "on")

    def _run_script(self, context: Dict):
        self._starttime = time.time()
        # execute the script
        with self.stdout as stdout, self.stderr as stderr:
            self._process = subprocess.Popen(
                ['bash', str(self.script)],
                stdout=stdout,
                stderr=stderr,
            )

            # save pid
            pid = self._process.pid
            progress = None

            if stdout == subprocess.PIPE:
                logger.info("Output from the job will be filtered")
                progress = ProgressReport(self._process)
                progress.start()

            try:
                self._process.wait(self.timeout)
            except subprocess.TimeoutExpired:
                import psutil
                parent = psutil.Process(pid)
                for child in parent.children(recursive=True):
                    child.kill()
                parent.kill()
                self._process.wait()
                logger.error(f"{pid} terminated ({self._process.returncode})")

        if progress:
            progress.stop()
            progress.join(5.0)

        self._endtime = time.time()
        self._handle_process_over(context)

        # run cleanup scripts
        if self.returncode != 0:
            self._handle_process_error(context)
        else:
            self._handle_run_success(context)

    def _handle_process_error(self, context: Dict):
        if self.on_failure:
            subprocess.Popen(["bash", str(self.on_failure_script)]).wait()

        # terminate on failure
        if self.continue_on_error:
            logger.warning(f"job {self.name} failed but still continuing...")
        else:
            raise JobError(f"Job {self.name} failed, terminating")

    def _handle_run_success(self, context: Dict):
        if self.on_success:
            subprocess.Popen(["bash", str(self.on_success_script)]).wait()

    def _handle_process_over(self, context: Dict):
        pass

    @property
    def workdir(self) -> Path:
        return self.project_config.workdir / ".cihpc" / f"{self.fullname}"

    @property
    def duration(self) -> float:
        return self._endtime - self._starttime

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

    def try_delete_after(self):
        if self.delete_after:
            if self.project_config.tmpdir.exists():
                logger.debug(f"cleaning {self.project_config.tmpdir}")
                shutil.rmtree(str(self.project_config.tmpdir), ignore_errors=True)
                return True
        return False

    @property
    def fullname(self):
        index_ord = chr(ord('A') + self.index)

        if self._variation:
            return f"{index_ord}.{self.name}-{self._variation}"
        else:
            return f"{index_ord}.{self.name}"

    @property
    def returncode(self) -> int:
        return self._process.returncode if self._process and self._process.returncode is not None else -1

    def __repr__(self):
        return f"<Job({self.fullname})>"