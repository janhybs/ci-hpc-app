import subprocess
from pathlib import Path
from typing import Dict, List, Union, Optional

from loguru import logger
from git import Repo
import os
import shutil

from cihpc.shared.utils.git_utils import GitRepo


class ProjectConfigGit:
    def __init__(self, data: Union[Dict, List, str]):
        self.deps: Dict[str, GitRepo] = dict()

        if isinstance(data, Dict):
            self.main_repo = self._from_dict(**data)

        elif isinstance(data, List):
            main = dict(url=data[0]) if isinstance(data[0], str) else data[0]
            self.main_repo = self._from_dict(**main)
            for dep in data[1:]:
                dep = dict(url=dep) if isinstance(dep, str) else dep
                repo = self._from_dict(**dep)
                self.deps[repo.name] = repo

        elif isinstance(data, str):
            self.main_repo = GitSpec(url=data)
            self.deps: Dict[str, GitRepo] = dict()

    @classmethod
    def _from_dict(cls, **kwargs) -> 'GitRepo':
        return GitRepo(
            url=kwargs['url'],
            commit=kwargs.get('commit', _default_commit),
            branch=kwargs.get('branch', _default_branch),
            reference=kwargs.get('reference', False),
        )

    def __repr__(self):
        return f'Git(main={self.main_repo}, deps={self.deps})'


_default_commit = None
_default_branch = "master"


class GitSpec:
    """
    :type repo: Optional[Repo]
    """

    clone_reference_cmd = 'git clone --bare'.split()

    def __init__(self, url, branch=_default_branch, commit=_default_commit, reference=False, **kwargs):
        self.url = url
        self.name = str(os.path.basename(url).split('.')[0])
        self._branch = branch
        self._commit = commit or None
        self.checkout = kwargs.get('checkout', True)
        self.clean_before_checkout = kwargs.get('clean-before-checkout', False)
        self.repo: Optional[Repo] = None
        self.reference = reference
        self._dir = kwargs.get('dir', None)

        self._fake_commit = None
        self._fake_branch = None

    def set_fake_head(self, commit=None, branch=None):
        self._fake_commit = commit
        self._fake_branch = branch
        return self

    def set_desired_head(self, commit=_default_commit, branch=_default_branch):
        self._branch = branch
        self._commit = commit
        return self

    @property
    def desired_branch(self):
        return self._branch

    @property
    def desired_commit(self):
        return self._commit

    @property
    def dir(self):
        return self._dir or os.path.abspath(os.path.join(os.getcwd(), self.name))

    def initialize(self):
        logger.info(f'Initializing repo {self.name} ({self.dir})')
        clone_args = {}

        if self.clean_before_checkout or self.reference:
            shutil.rmtree(self.dir, ignore_errors=True)

        if self.reference:
            reference_path = Path(f'{str(self.dir)}.git')
            if not reference_path.exists():
                cmd = self.clone_reference_cmd + [self.url, str(reference_path)]
                result = subprocess.run(cmd)

            clone_args['reference'] = str(reference_path)

        if not self.checkout:
            self.repo = Repo(self.dir)
        else:
            if os.path.exists(self.dir):
                self.repo = Repo(self.dir)
            else:
                self.repo = Repo.clone_from(
                    self.url,
                    self.dir,
                    **clone_args
                )

            self.repo.remote().fetch()
            self.branches = [branch.name for branch in self.repo.heads]
            print(f"{self.branches}")

            # easy scenario, branch set, commit not
            if self._branch and not self._commit:
                logger.info(f'Checking out branch {self._branch}')
                # branch must exists
                self.repo.head.reference = self.repo.create_head('_temp_', force=True)

                try:
                    self.repo.delete_head(self._branch, force=True)
                    self.repo.git.checkout(self._branch, force=True)
                except:
                    self.repo.git.checkout(self._branch, force=True)

                self.repo.delete_head('_temp_', force=True)

                self.repo.active_branch.set_tracking_branch(self.repo.remote().refs[self._branch])
                self.repo.remote().pull(self._branch)

            # also easy, we have the commit but not the branch
            # only the branch name will be **detached**
            elif not self._branch and self._commit:
                logger.info(f'Checking out {self._commit} under branch DETACHED!')
                self.repo.git.checkout(self._commit, force=True)

            # both branch and commit are set
            # we checkout to commit and create local only branch
            elif self._branch and self._commit:
                logger.info(f'Checking out {self._commit} under branch {self._branch}')
                self.repo.git.checkout(self._commit, force=True)
                try:
                    self.repo.delete_head(self._branch, force=True)
                except:
                    pass
                new_branch = self.repo.create_head(self._branch)
                self.repo.head.reference = new_branch

            # nothing was specified
            # we go to the latest master
            else:
                logger.info(f'Checking out the latest commit (branch master)')
                self._branch = 'master'
                self.repo.git.checkout(self._branch, force=True)
                self.repo.active_branch.set_tracking_branch(self.repo.remote().refs[self._branch])
                self.repo.remote().pull(self._branch)

    @property
    def branch(self) -> str:
        try:
            return self._fake_branch or str(self.repo.active_branch.name)
        except:
            return f'detached-at-{self.commit[:8]}'

    @property
    def commit(self) -> str:
        return self._fake_commit or str(self.repo.head.commit.hexsha)

    @property
    def commit_short(self) -> str:
        return self.commit[:8]

    @property
    def head_commit(self):
        return self.repo.head.commit

    def index_info(self):
        head = self.repo.head
        return f'{self.branch}:{head.commit.hexsha[:8]} by <{head.commit.author}> on {head.commit.authored_datetime}'

    def _checkout(self):
        pass

    def __repr__(self):
        if self.repo:
            return f'Repo({self.url} @ {self.branch}:{self.commit})'
        return f'Repo({self.url} @ {self._branch}:{self._commit})'
