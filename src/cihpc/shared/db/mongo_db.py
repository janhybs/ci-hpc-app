from typing import Dict, Union, Type, List, Callable

import pymongo
from loguru import logger
from pymongo import MongoClient

from cihpc.shared.db.cols.col_index_info import ColIndexInfo
from cihpc.shared.db.cols.col_index_stat import ColIndexStat
from cihpc.shared.db.cols.col_repo_info import ColRepoInfo
from cihpc.shared.db.cols.col_schedule import ColSchedule
from cihpc.shared.db.cols.col_timers import ColTimer
from cihpc.shared.db.models import IdEntity
from cihpc.shared.db.timer_index import TimerIndex
from cihpc.shared.errors.config_error import ConfigError
from cihpc.shared.g import G

AllColTypes = Union[IdEntity, ColIndexInfo, ColSchedule, ColTimer, ColIndexStat, ColRepoInfo]
MatchType = Union[TimerIndex, Dict]

_timer_index_keys = list(TimerIndex().keys())


def in_list(items):
    return {"$in": items}


class MongoCollection:
    def __init__(self, collection: pymongo.collection.Collection, factory: Type[IdEntity]):
        self._collection = collection
        self._factory = factory
        self.name = collection.name

    def find(self, index: MatchType, projection: List = None, raw=False, **kwargs) -> List[AllColTypes]:
        match = dict()
        for k, v in index.items():
            if v is not None or raw:
                if k in _timer_index_keys and not raw:
                    match[f"index.{k}"] = v
                else:
                    match[f"{k}"] = v

        for item in self._collection.find(match or {}, projection):
            yield self._factory.from_dict(item)

    def insert(self, value: AllColTypes, **kwargs):
        return self._collection.insert_one(value, **kwargs)

    def insert_many(self, documents: List[AllColTypes], **kwargs):
        return self._collection.insert_many(documents, **kwargs)

    def aggregate(self, pipeline: List[Dict], **kwargs) -> List[AllColTypes]:
        return self._collection.aggregate(pipeline, **kwargs)

    def update(self, document: AllColTypes, updates: Dict = None, **kwargs):
        if not updates:
            updates = kwargs

        return self._collection.update_one(
            dict(_id=document.id),
            {"$set": {k: v for k, v in updates.items()}}
        )

    def batch_replace(self, documents: List[AllColTypes]):
        for document in documents:
            if isinstance(document, IdEntity):
                yield self._collection.replace_one(
                    dict(_id=document.id),
                    document
                )
            else:
                yield self._collection.replace_one(
                    dict(_id=document["_id"]),
                    document
                )

    def batch_update(self, documents: List[AllColTypes], match: Callable[[AllColTypes], dict], replace: Callable[[AllColTypes], dict]):
        for d in documents:
            yield self._collection.update_one(
                match(d),
                {"$set": replace(d)}
            )

    def __repr__(self):
        return f"<Col({self.name})>"

    @property
    def collection(self):
        return self._collection


class MongoImpl(object):
    """
    Class Mongo manages connection and queries

    :type client: MongoClient
    :type col_timers: MongoColTimer
    :type col_scheduler: MongoColSchedule
    :type col_index_stat: MongoColIndexStat
    :type col_index_info: MongoColIndexInfo
    :type col_repo_info: MongoColRepoInfo
    """

    def __init__(self, project_name):
        self.project_name = project_name
        self.config = G.get_secret(self.project_name)
        if not self.config:
            raise ConfigError("Could not find db configuration")

        self.config_database = self.config.get("database", {})
        self.config_artifacts = self.config.get("artifacts", {})

        # create connection dict
        self.config_database['connect'] = True
        if 'type' in self.config_database:
            self.config_database.pop('type')
        self.client = MongoClient(**self.config_database)

        # select db and cols
        self.db = self.db = self.client.get_database(self.config_artifacts.get("db_name", "timers"))

        # noinspection PyTypeChecker
        self.col_timers = MongoCollection(
            self.db.get_collection(self.config_artifacts.get('col_timers_name', f'timers-{G.version}')),
            ColTimer
        )
        # noinspection PyTypeChecker
        self.col_index_info = MongoCollection(
            self.db.get_collection(self.config_artifacts.get('col_index_info_name', f'indexinfo-{G.version}')),
            ColIndexInfo
        )
        # noinspection PyTypeChecker
        self.col_repo_info = MongoCollection(
            self.db.get_collection(self.config_artifacts.get('col_repo_info_name', f'repoinfo-{G.version}')),
            ColRepoInfo
        )
        # noinspection PyTypeChecker
        self.col_index_stat = MongoCollection(
            self.db.get_collection(self.config_artifacts.get('col_index_stat_name', f'indestat-{G.version}')),
            ColIndexStat
        )
        # noinspection PyTypeChecker
        self.col_scheduler = MongoCollection(
            self.db.get_collection(self.config_artifacts.get('col_scheduler_name', f'scheduler-{G.version}')),
            ColSchedule
        )

        logger.debug(
            f'connected: {self}, {self.db.name}:{{{self.col_timers.name}, {self.col_index_info.name}, {self.col_scheduler.name}}}')

        self.ensure_index()

    def ensure_index(self):
        result = self.col_repo_info.collection.create_index(
            "commit",
            unique=True,
            name="unique_commit"
        )
        logger.info(f"created index {result}")

    def __repr__(self):
        return f'Mongo({self.client.address[0]}:{self.client.address[1]})'


class Mongo:
    _instances: Dict[str, MongoImpl] = dict()
    _default_project_name: str = None

    @classmethod
    def set_default_project(cls, project_name):
        cls._default_project_name = project_name

    def __new__(cls, *args, **kwargs):
        if not cls._instances:
            if cls._default_project_name:
                cls._instances[cls._default_project_name] = MongoImpl(cls._default_project_name)

        return next(iter(cls._instances.values()))


class MongoColTimer(MongoCollection):
    def find(self, match: MatchType = None, projection: List = None, **kwargs) -> List[ColTimer]:
        return super().find(match, projection, **kwargs)

    def aggregate(self, pipeline: List[Dict], **kwargs) -> List[ColTimer]:
        return super().aggregate(pipeline, **kwargs)


class MongoColSchedule(MongoCollection):
    def find(self, match: MatchType = None, projection: List = None, **kwargs) -> List[ColSchedule]:
        return super().find(match, projection, **kwargs)

    def aggregate(self, pipeline: List[Dict], **kwargs) -> List[ColSchedule]:
        return super().aggregate(pipeline, **kwargs)


class MongoColIndexStat(MongoCollection):
    def find(self, match: MatchType = None, projection: List = None, **kwargs) -> List[ColIndexStat]:
        return super().find(match, projection, **kwargs)

    def aggregate(self, pipeline: List[Dict], **kwargs) -> List[ColIndexStat]:
        return super().aggregate(pipeline, **kwargs)


class MongoColIndexInfo(MongoCollection):
    def find(self, match: MatchType = None, projection: List = None, **kwargs) -> List[ColIndexInfo]:
        return super().find(match, projection, **kwargs)

    def aggregate(self, pipeline: List[Dict], **kwargs) -> List[ColIndexInfo]:
        return super().aggregate(pipeline, **kwargs)


class MongoColRepoInfo(MongoCollection):
    def find(self, index: MatchType = None, projection: List = None, **kwargs) -> List[ColRepoInfo]:
        return super().find(index, projection, **kwargs)

    def aggregate(self, pipeline: List[Dict], **kwargs) -> List[ColRepoInfo]:
        return super().aggregate(pipeline, **kwargs)

    def insert(self, value: ColRepoInfo, **kwargs):
        return super().insert(value, **kwargs)

    def insert_many(self, documents: List[ColRepoInfo], **kwargs):
        return super().insert_many(documents, **kwargs)
