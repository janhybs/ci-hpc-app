from pathlib import Path
from typing import Dict, List, Type
import glob

from loguru import logger

from cihpc.collectors import ICollector, GenericJsonCollector
from cihpc.collectors.flow123d import Flow123dCollector
from cihpc.config.configure import configure, configure_recursive
from cihpc.shared.db.cols.col_timers import ColTimer
from cihpc.shared.db.mongo_db import Mongo
from cihpc.shared.utils.data_util import ensure_list


_collectors: Dict[str, Type[ICollector]] = {
    'flow123d': Flow123dCollector,
    'generic-json': GenericJsonCollector,
}


class ProjectConfigCollect:
    def __init__(self, data: Dict):
        if not data:
            self.enabled = False
        else:
            self.enabled = True
            self.files: List[str] = ensure_list(data.get("files", []))
            self.delete_after: bool = data.get("delete-after", False)
            self.extra = data.get("extra", {})
            self.module = data.get("module", "generic-json")
            self.save_to_db = data.get("save-to-db", True)

    def __bool__(self):
        return self.enabled

    def execute(self, context: Dict):
        extra = configure_recursive(self.extra, context)

        files = list()
        for file in self.files:
            path = Path(configure(file, context, False)).absolute()
            files.extend(glob.glob(str(path), recursive=True))

        collector_type = _collectors[self.module]
        collector = collector_type(context, extra)

        for file in files:
            try:
                reports = collector.process_file(Path(file))
            except Exception as e:
                logger.info(f"Failed to obtain timers from {file} using {collector_type}: {e}")
                logger.debug(Path(file).read_text())
                continue

            # convert to ColTimer
            timers = [ColTimer(**report) for report in reports]

            if not timers:
                logger.info(f"Did not found any timers in {file}")
                continue

            if self.save_to_db:
                # save to db
                try:
                    Mongo().col_timers.insert_many(timers)
                except Exception as e:
                    logger.error(f"Failed to save data to db: {e}")

            for timer in timers:
                yield timer.index

