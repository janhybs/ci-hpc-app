from subprocess import Popen
from threading import Thread
import re
from typing import Callable

from loguru import logger

from cihpc.shared.utils.throttle import throttle

_percent_regex = re.compile(r"\[\s*(\d+)%\s*\]\s*(.*)")


def _default_callable(x: str, y: str):
    p = int(x)
    print(f"[{p:3d}%] - {y}")

def try_next_line(stdout):
    try:
        line = stdout.readline()
        if not line:
            return None
        return line.decode()
    except Exception as e:
        logger.error(f"Error while reading line: {e}")
        return None

class ProgressReport(Thread):
    def __init__(self, process: Popen, callback: Callable = _default_callable):
        super().__init__()
        self.is_running = True
        self.process = process
        self.callback = callback
        self.is_broken = False

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
                    line = try_next_line(self.process.stdout)
                    if line is None:
                        logger.exception("no line")
                        break
                    
                    if(line.find(" error: ") != -1):
                        self.is_broken = True

                    if self.is_broken:
                        print(line.strip())
                    else:
                        matches = _percent_regex.findall(line)
                        if matches and self.callback:
                            self.invoke_callable(*matches[0])
                except Exception as e:
                    logger.error(f"Error while reading line: {e}")
                    break

        monitor = Thread(target=read_stdout)
        monitor.start()
        monitor.join()
