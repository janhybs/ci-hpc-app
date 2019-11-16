import re
from pathlib import Path
from typing import Dict
import json

from loguru import logger
from cihpc.collectors import ICollector


_flow123d_field_sums_float = {
    'duration': 'cumul-time-sum',
    'executed': 'call-count-sum',
    'cnt_alloc': 'memory-alloc-called-sum',
    'cnt_dealloc': 'memory-dealloc-called-sum',
    'mem_alloc': 'memory-alloc-sum',
    'mem_dealloc': 'memory-dealloc-sum',
}

_flow123d_field_maps = {
    'file_path': 'file-path',
    'function': 'function',
}


class Flow123dCollector(ICollector):
    _children = 'children'

    def __init__(self, context: Dict, extras: Dict):
        super().__init__(context, extras)

    def process_file(self, file: Path):
        try:
            data = json.loads(file.read_text())
        except Exception as e:
            logger.error(f"Could not parse profiler {e}")
            return None

        problem = dict()
        # grab task size as well
        problem["task_size"] = int(data['task-size'])

        # get cpu
        cpus = float(data['run-process-count'])
        problem['cpus'] = cpus

        # grab the root
        root = data[self._children][0]
        result = self._extract_important(root, cpus=cpus)
        # and traverse the children
        timers = self._traverse(root, list())

        run_reports = list()

        for timer in timers:
            timer_report = dict(
                index=self.extras.copy(),
                system=self.system,
                problem=problem,
                result=timer,
            )
            timer_report['index']['frame'] = timer_report['result']['name']
            run_reports.append(timer_report)

        return run_reports

    @classmethod
    def _normalise_tag_name(cls, tag: str):
        return re.sub('[_-]+', '-',
                      re.sub("([a-z])([A-Z])", "\g<1>-\g<2>", tag) \
                      .replace('::', '-') \
                      .replace(' ', '-').lower()
                      )

    def _traverse(self, root, result, path=''):
        path = path + '/' + self._normalise_tag_name(root['tag'])

        item = self._extract_important(root)
        item['path'] = path

        result.append(item)

        if self._children in root:
            for child in root[self._children]:
                self._traverse(child, result, path)

        return result

    @classmethod
    def _extract_important(cls, child, cpus=1.0):
        result = dict()
        result.update({k: float(child[v]) / cpus for k, v in _flow123d_field_sums_float.items()})
        result.update({k: child[v] for k, v in _flow123d_field_maps.items()})

        result['name'] = cls._normalise_tag_name(child['tag'])
        result['file_line'] = int(child['file-line'])
        result['dur_ratio'] = float(child['cumul-time-min']) / float(child['cumul-time-max'])
        return result
