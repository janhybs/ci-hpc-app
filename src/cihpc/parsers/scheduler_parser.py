from cihpc.parsers.common_parser import CommonParser


class SchedulerParser(CommonParser):
    per_branch: int = 10

    def add_arguments(self):
        super().add_arguments()
        self.add_argument("-n", "--per-branch", type=int, default=10, dest="per_branch")
