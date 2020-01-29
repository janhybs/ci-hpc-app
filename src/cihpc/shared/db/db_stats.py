import json
from typing import Dict, List, Tuple

from loguru import logger

from cihpc.shared.db.cols.col_schedule import ColScheduleStatus
from cihpc.shared.db.mongo_db import Mongo


class DBStats:
    def __init__(self):
        pass

    @staticmethod
    def _try_execute(func, default):
        try:
            return func(Mongo())
        except Exception as e:
            logger.warning(f"Mongo command failed: {e}")
            return default

    @classmethod
    def get_broken_count(cls, index: Dict) -> int:
        info = cls.get_index_info(index)
        return len(info) - info.count(0)

    @classmethod
    def get_run_count(cls, index: Dict) -> Tuple[int, int]:
        index_copy = index.copy()
        index_copy["branch"] = None
        info = cls.get_index_info(index_copy)
        return info.count(0), len(info) - info.count(0)

    @classmethod
    def get_index_info(cls, index: Dict) -> List[int]:
        """
        https://docs.mongodb.com/manual/core/aggregation-pipeline/
        https://docs.mongodb.com/manual/reference/operator/aggregation/group/
        :param index:
        :return:
        """
        match = dict()
        for k, v in index.items():
            if v is not None:
                match[f"index.{k}"] = v

        pipeline = [
            {"$match": match},
            {"$group": {
             "_id": None,
             "returncode": {"$push": "$run.returncode"},
             "duration": {"$push": "$run.duration"},
            }}
        ]
        result = cls._try_execute(lambda mongo: mongo.col_index_info.aggregate(pipeline), [dict(returncode=[])])
        for item in result:
            return item.get("returncode")

        return []

    @classmethod
    def get_schedule_repetitions(cls, index: Dict, status=ColScheduleStatus.NotProcessed) -> int:
        match = dict()
        for k, v in index.items():
            if v is not None and k != "branch":
                match[f"index.{k}"] = v

        match["status"] = status

        pipeline = [
            {"$match": match},
            {"$group": {
             "_id": None,
             "repetitions": {"$sum": "$details.repetitions"},
            }}
        ]
        # print(f"{json.dumps(pipeline, indent=4)}")
        result = cls._try_execute(lambda mongo: mongo.col_scheduler.aggregate(pipeline), [dict(repetitions=0)])
        for item in result:
            return item.get("repetitions")

        return 0

        #
        # return self.mongo.col_index_info.find(
        #     match=match,
        #     projection=dict(
        #         run=1,
        #     )
        # )
