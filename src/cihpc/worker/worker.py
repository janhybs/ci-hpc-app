from cihpc.config import read_cfg
from cihpc.parsers.main import parse_worker_args
from cihpc.shared.db.cols.col_index_info import ColIndexInfo
from cihpc.shared.db.mongo_db import Mongo
from cihpc.shared.g import G

if __name__ == '__main__':
    args = parse_worker_args()

    # read yaml
    G.init(args)
    config = read_cfg(args.config_file)
    Mongo.set_default_project(config.name)

    config.execute()
