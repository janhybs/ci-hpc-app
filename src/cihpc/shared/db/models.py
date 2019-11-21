#!/bin/python3
# author: Jan Hybs
from typing import Any, Dict, Type

from bson import ObjectId

from cihpc.shared.utils import data_util


class Fields(object):
    GIT_DATETIME = 'git-datetime'
    TEST_SIZE = 'test-size'
    GIT_TIMESTAMP = 'git-timestamp'
    UUID = 'uuid'
    ID = '_id'
    GIT_COMMIT = 'git-commit'
    DURATION = 'duration'


class Entity(dict):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def from_dict(cls, value: dict) -> 'Entity':
        return cls(**value)

    def __setattr__(self, key: str, value: any):
        self[key] = value

    def __getattr__(self, key: str) -> any:
        return self[key]

    def __setitem__(self, key: str, value: any):
        parts = key.split('.')
        if len(parts) == 1:
            super().__setitem__(key, value)
        else:
            first = parts[0]
            if first not in self:
                self.__setitem__(first, {})

            root = self.__getitem__(first)
            for part in parts[1:-1]:
                root[part] = root.get(part, {})
                root = root[part]
            root[parts[-1]] = value

    def __getitem__(self, key: str) -> any:
        parts = key.split('.')
        if len(parts) == 1:
            return super().__getitem__(key)
        else:
            first = parts[0]
            root = self.__getitem__(first)
            for part in parts[1:-1]:
                root[part] = root.get(part, {})
                root = root[part]
            return root.get(parts[-1])


class IdEntity(Entity):
    """
    :type _id: bson.ObjectId
    """

    def __init__(self, **kwargs):
        self._id = ObjectId()
        super().__init__(**kwargs)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value
