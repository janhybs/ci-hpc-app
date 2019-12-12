from subprocess import Popen
from threading import Thread
import re
from typing import Callable

from loguru import logger

from cihpc.shared.utils.throttle import throttle

_percent_regex = re.compile(r"\[\s*(\d+)%\s*\]")


def _default_callable(x: int):
    logger.info(f"Progress: {x:3d}%")


class ProgressReport(Thread):
    def __init__(self, process: Popen, callback: Callable = _default_callable):
        super().__init__()
        self.is_running = True
        self.process = process
        self.callback = callback

    def stop(self):
        self.is_running = False

    @throttle(seconds=1)
    def invoke_callable(self, *args, **kwargs):
        if self.callback:
            self.callback(*args, **kwargs)

    def run(self):
        def read_stdout():
            while self.is_running:
                try:
                    line: bytes = self.process.stdout.readline()
                    if not line:
                        break
                    else:
                        matches = _percent_regex.findall(line.decode())
                        if matches and self.callback:
                            self.invoke_callable(int(matches[0]))
                except Exception as e:
                    logger.error(f"Error while reading line: {e}")
                    break

        monitor = Thread(target=read_stdout)
        monitor.start()
        monitor.join()
