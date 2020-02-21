from cihpc.parsers.common_parser import CommonParser
import maya


class RepoInfoParser(CommonParser):
    per_branch: int = 25
    max_age: maya.MayaDT = maya.when("24 months ago")
    only: str = None

    def add_arguments(self):
        super().add_arguments()
        self.add_argument("-n", "--per-branch", dest="per_branch", type=int)
        self.add_argument("-m", "--max-age", dest="max_age", type=maya.when)
