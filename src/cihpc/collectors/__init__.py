import json
import subprocess
from pathlib import Path
from typing import Dict, List

from loguru import logger

from cihpc.shared.utils import data_util


def _run(cmd, line=None):
    lines = subprocess.check_output(cmd, shell=True).decode().strip().splitlines()
    if line:
        for l in lines:
            if l.startswith(line):
                return l[len(line):].replace('"', '')
    return lines[0].replace('"', '')


def unwind_report(report: Dict, unwind_from='timers', unwind_to='timer', flatten=False):
    """
    Method will convert flatten json report format to a list of reports

    Parameters
    ----------
    report : Dict
        object which will be unwinded
    unwind_from : str
        key name which contains list of values
    unwind_to : str
        under what name to store list values
    flatten : str
        if set, will flatten the documents using this value as separator
    """
    items = list()
    report_copy = report.copy()
    timers = report_copy.pop(unwind_from)
    for timer in timers:
        item = report_copy.copy()
        item[unwind_to] = timer
        if flatten:
            items.append(data_util.flatten(item, sep=flatten))
        else:
            items.append(item)
    return items


def unwind_reports(reports: List[Dict], unwind_from='timers', unwind_to='timer', flatten=False):
    """
    Method will convert flatten json reports format to a list of reports

    Parameters
    ----------
    reports : List[Dict]
        objects which will be unwinded
    unwind_from : str
        key name which contains list of values
    unwind_to : str
        under what name to store list values
    flatten : str
        if set, will flatten the documents using this value as separator

    """
    items = list()
    for report in reports:
        items.extend(unwind_report(report, unwind_from, unwind_to, flatten))
    return items


class ICollector:
    def __init__(self, context: Dict, extras: Dict):
        self.context = context
        self.extras = extras

        self.system = dict(
            name=_run('uname'),
            hostname=_run('hostname'),
            os_name=_run('cat /etc/*-release', 'VERSION='),
            os_version=_run('cat /etc/*-release', 'NAME='),
            username=_run('echo $(whoami):$(id -u):$(id -g)'),
        )

    def process_file(self, file: Path) -> List[Dict]:
        raise NotImplemented()


class GenericJsonCollector(ICollector):
    def process_file(self, file: Path) -> List[Dict]:
        try:
            data = json.loads(file.read_text())
        except Exception as e:
            logger.error(f"Could not parse profiler {e}")
            return []

        reports = unwind_report(data)
        run_reports = list()

        for report in reports:
            timer_report = dict(
                index=self.extras.copy(),
                system=self.system,
                problem=report["problem"],
                result=report["timer"],
            )
            timer_report['index']['frame'] = timer_report['result']['name']
            run_reports.append(timer_report)

        return run_reports

