from cihpc.parsers.scheduler_parser import SchedulerParser
from cihpc.parsers.worker_parser import WorkerParser


def parse_worker_args(args=None) -> WorkerParser:
    return WorkerParser(args).parse_args(args)


def parse_scheduler_args(args=None) -> SchedulerParser:
    return SchedulerParser(args).parse_args(args)
