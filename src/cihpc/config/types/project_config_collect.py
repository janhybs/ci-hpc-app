from pathlib import Path
from typing import Dict, List
import glob

from cihpc.collectors.flow123d import Flow123dCollector
from cihpc.config.configure import configure, configure_recursive
from cihpc.shared.db.cols.col_timers import ColTimer
from cihpc.shared.utils.data_util import ensure_list


class ProjectConfigCollect:
    def __init__(self, data: Dict):
        if not data:
            self.enabled = False
        else:
            self.enabled = True
            self.files: List[str] = ensure_list(data.get("files", []))
            self.delete_after: bool = data.get("delete-after", False)
            self.extra = data.get("extra", {})
            self.module = data.get("module")

    def __bool__(self):
        return self.enabled

    def execute(self, context: Dict):
        extra = configure_recursive(self.extra, context)

        files = list()
        for file in self.files:
            path = Path(configure(file, context, False)).absolute()
            files.extend(glob.glob(str(path), recursive=True))

        collector = Flow123dCollector(context, extra)
        for file in files:
            reports = collector.process_file(Path(file))
            timers = [ColTimer(**report) for report in reports]
            print(timers[0].system)
            # TODO add to DB

