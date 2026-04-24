import json
import sys

sys.path.append("..")
import json
import logging

from common_packages.db_utils import ClickhouseOperator
from tests import get_config

logging.basicConfig(level=logging.INFO)


class TestClickhouseOperator:
    def test_clickhouse(self):
        config: dict = get_config()
        ck = ClickhouseOperator(**config["db"]["clickhouse"])
        tables: set[str] = ck.fetch_all_tables()
        # print(tables)

        data = ck.fetch_specify_sql_data(
            "select * from `detector-anomaly` limit 5;", replace_nonwords=False
        )
        # print(data)

        d = data[0]

        d2 = ck.convert_datatype_for_ck(data[0])

        ck.insert_specify_sql("INSERT INTO `detector-anomaly` VALUES", d2)
