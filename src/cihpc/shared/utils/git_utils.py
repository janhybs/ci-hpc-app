#!/bin/python3
# author: Jan Hybs

from git import Repo, RemoteReference, Head, Commit
from typing import List, Union
from dataclasses import dataclass, field
import maya


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


def iter_revision(repo: Repo, revision: Union[Head, str], limit=10) -> List[Commit]:
    if isinstance(revision, Head):
        rev = revision.name
    elif isinstance(revision, str):
        rev = revision
    else:
        rev = revision

    for i, cmt in enumerate(repo.iter_commits(rev=rev)):
        if i >= limit:
            break
        yield cmt
