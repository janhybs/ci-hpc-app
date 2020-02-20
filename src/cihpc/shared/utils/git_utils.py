#!/bin/python3
# author: Jan Hybs
import os
from pathlib import Path

from git import Repo, RemoteReference, Head, Commit
from typing import List, Union, Optional
from dataclasses import dataclass, field
import maya
from loguru import logger

from cihpc.shared.utils import string_util

default_min_age = maya.when('6 months ago')


@dataclass(order=True, unsafe_hash=True, eq=True, repr=False)
class Branch:
    head: Head = field(compare=False, hash=True)
    date: maya.MayaDT = field(compare=True, hash=False)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.date.datetime(naive=True)}, {self.head.name})'


@dataclass(order=False, unsafe_hash=True, eq=True, repr=False)
class BranchCommit:
    commit: Commit = field(compare=False, hash=True)
    branch: Branch = field(compare=False, hash=False)

    def __lt__(self, other: 'BranchCommit'):
        return other.commit.authored_datetime > self.commit.authored_datetime

    def __le__(self, other: 'BranchCommit'):
        return other.commit.authored_datetime >= self.commit.authored_datetime

    def __gt__(self, other: 'BranchCommit'):
        return other.commit.authored_datetime < self.commit.authored_datetime

    def __ge__(self, other: 'BranchCommit'):
        return other.commit.authored_datetime <= self.commit.authored_datetime

    def __iter__(self):
        return iter((self.branch, self.commit))

    def __repr__(self):
        return f'{self.__class__.__name__}({self.commit} {self.commit.authored_datetime}, {self.branch})'


def get_active_branches(repo: Repo, min_age=default_min_age) -> List[Branch]:
    for branch in repo.remotes.origin.refs:
        head: RemoteReference = branch
        remote_date = extract_date_from_head(head)
        is_old = min_age is not None and remote_date < min_age

        if is_old:
            continue

        yield Branch(head, remote_date)


def extract_date_from_head(head: Head):
    return maya.MayaDT.from_datetime(head.commit.authored_datetime)


def iter_revision(repo: Repo, revision: Union[Head, str], limit=10, **kwargs) -> List[Commit]:
    if isinstance(revision, Head):
        rev = revision.name
    elif isinstance(revision, str):
        rev = revision
    else:
        rev = revision

    # basically no limit
    if limit < 0:
        limit = 10**10

    for i, cmt in enumerate(repo.iter_commits(rev=rev, **kwargs)):
        if i >= limit:
            break
        yield cmt


class GitRepo:
    def __init__(self, url: str, commit=None, branch="master", **kwargs):
        self.url = url
        self.name = str(os.path.basename(url).split('.')[0])
        self._desired_commit = commit
        self._desired_branch = branch
        self._fake_commit = None
        self._fake_branch = None
        self.repo: Optional[Repo] = None
        self._dir = None

    def set_fake_head(self, commit: str, branch: str):
        self._fake_commit = commit
        self._fake_branch = branch
        return self

    def set_desired_head(self, commit: str, branch: str):
        self._desired_branch = branch
        self._desired_commit = commit
        return self

    def _checkout(self, commit: str):
        self.repo.git.checkout(commit, force=True)

    def _set_branch(self, branch: str, track=False) -> Head:
        new_branch = self.repo.create_head(branch)
        self.repo.head.reference = new_branch
        if track:
            new_branch.set_tracking_branch(self.repo.remote().refs[branch])
        return new_branch

    def _delete_branch(self, branch: str):
        try:
            self.repo.delete_head(branch, force=True)
        except:
            pass

    def initialize(self):
        logger.info(f'Initializing repo {self.name} ({self.dir})')

        if self.dir.exists():
            self.repo = Repo(str(self.dir))
        else:
            self.repo = Repo.clone_from(
                self.url,
                self.dir,
            )

        # fetch latest
        self.repo.remote().fetch()
        random_name = f"tmp_{string_util.rand_str()}"

        if self._desired_commit:
            self._checkout(self._desired_commit)
            random_branch = self._set_branch(random_name)
            self._delete_branch(self._desired_branch)
            random_branch.rename(self._desired_branch, force=True)
            self._set_branch(self._desired_branch, track=True)
        else:
            self._set_branch(random_name)
            self._delete_branch(self._desired_branch)
            self._checkout(self._desired_branch)
            self._set_branch(self._desired_branch, track=True)
            self._delete_branch(random_name)

    @property
    def dir(self):
        return self._dir or Path(os.path.abspath(os.path.join(os.getcwd(), self.name)))

    @property
    def branch(self) -> str:
        try:
            return self._fake_branch or self.actual_branch or self._desired_branch
        except:
            return f'detached-at-{self.commit[:8]}'

    @property
    def commit(self) -> str:
        return self._fake_commit or self.actual_commit or self._desired_commit

    @property
    def actual_commit(self):
        try:
            return str(self.repo.head.commit.hexsha)
        except:
            return None

    @property
    def actual_branch(self):
        if self.repo:
            try:
                return str(self.repo.active_branch.name)
            except:
                return f'detached-at-{self.commit[:8]}'
        return None

    @property
    def commit_short(self) -> str:
        return self.commit[:8]

    def __repr__(self):
        if self.repo:
            return f'Repo({self.url} @ {self.branch}:{self.commit})'
        return f'Repo({self.url} @ {self._desired_branch}:{self._desired_commit})'
