import subprocess
from typing import Optional, TextIO, Union


class IStreamable:

    def __init__(self, target: Optional[Union[str, int]] = None):
        self.target: Optional[Union[str, int]] = target
        self.fp = None

    def open(self):
        pass

    def close(self):
        pass

    def __enter__(self) -> Optional[TextIO]:
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


class StreamableFile(IStreamable):
    def open(self):
        self.fp = open(self.target, 'w')
        return self.fp

    def close(self):
        self.fp.close()


class StreamableSpecial(IStreamable):
    def open(self):
        if self.target in (1, subprocess.STDOUT, "stdout"):
            self.fp = subprocess.STDOUT

        if self.target in (0, subprocess.DEVNULL, "devnull", False):
            self.fp = subprocess.DEVNULL

    def close(self):
        pass


def get_streamable(type: Optional[str]) -> IStreamable:
    if type in (None, False):
        return IStreamable()

    if isinstance(type, int) or type in ("stdout", "devnull", subprocess.DEVNULL, subprocess.STDOUT):
        return StreamableSpecial(type)

    if isinstance(type, str):
        return StreamableFile(type)

    return IStreamable()
