from typing import Dict, Union, Type, List

import pymongo
from loguru import logger
from pymongo import MongoClient

from cihpc.shared.db.cols.col_index_info import ColIndexInfo
from cihpc.shared.db.cols.col_index_stat import ColIndexStat
from cihpc.shared.db.cols.col_schedule import ColScheduler
from cihpc.shared.db.cols.col_timers import ColTimer
from cihpc.shared.db.models import IdEntity
from cihpc.shared.errors.config_error import ConfigError
from cihpc.shared.g import G


AllColTypes = Union[IdEntity, ColIndexInfo, ColScheduler, ColTimer]


class MongoCollection:
    def __init__(self, collection: pymongo.collection.Collection, factory: Type[IdEntity]):
        self._collection = collection
        self._factory = factory
        self.name = collection.name

    def find(self, match: dict = None, projection: list = None) -> List[AllColTypes]:
        for item in self._collection.find(match or {}, projection):
            yield self._factory.from_dict(item)

    def insert(self, value: AllColTypes, **kwargs):
        return self._collection.insert_one(value, **kwargs)

    def insert_many(self, documents: List[AllColTypes], **kwargs):
        return self._collection.insert_many(documents, **kwargs)

    def __repr__(self):
        return f"<Col({self.name})>"

class MongoImpl(object):
    """
    Class Mongo manages connection and queries

    :type client: MongoClient
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

        self.col_timers = MongoCollection(
            self.db.get_collection(self.config_artifacts.get('col_timers_name', f'timers-{G.version}')),
            ColTimer
        )
        self.col_index_info = MongoCollection(
            self.db.get_collection(self.config_artifacts.get('col_index_info_name', f'indexinfo-{G.version}')),
            ColIndexInfo
        )
        self.col_index_stat = MongoCollection(
            self.db.get_collection(self.config_artifacts.get('col_index_stat_name', f'indestat-{G.version}')),
            ColIndexStat
        )
        self.col_scheduler = MongoCollection(
            self.db.get_collection(self.config_artifacts.get('col_scheduler_name', f'scheduler-{G.version}')),
            ColScheduler
        )

        logger.debug(f'connected: {self}, {self.db.name}:{{{self.col_timers.name}, {self.col_index_info.name}, {self.col_scheduler.name}}}')

    def __repr__(self):
        return 'Mongo({self.client.address[0]}:{self.client.address[1]})'.format(self=self)


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
