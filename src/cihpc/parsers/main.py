from cihpc.parsers.worker_parser import WorkerParser


def parse_worker_args(args=None) -> WorkerParser:
    WorkerParser(args).print_usage()
    return WorkerParser(args).parse_args(args)
