from typing import NoReturn, Optional, Union

try:
    import numpy
    import pandas as pd
    from clickhouse_driver import Client
except ImportError as exc:
    raise ImportError(
        "Couldn't import pandas clickhouse_driver. pip install --upgrade pandas clickhouse-driver numpy"
    ) from exc

from pandas import DataFrame, Series, Timedelta, Timestamp
from pandas.core.dtypes.dtypes import CategoricalDtype


class ClickhouseOperator:
    """Clickhouse 数据库的操作封装"""

    def __init__(self, **kwargs) -> None:
        if not {"host", "port", "user", "password", "database"}.issubset(kwargs.keys()):
            raise ValueError("host,port,user,password,database must be provided")
        self.host = kwargs["host"]
        self.port = kwargs["port"]
        self.user = kwargs["user"]
        self.password = kwargs["password"]
        self.database = kwargs["database"]

        self.client = Client(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            settings={"use_numpy": True},
        )

    def fetch_all_tables(self) -> set[str]:
        """获取所有表名"""
        sql = "SHOW TABLES"
        data: DataFrame = self.client.query_dataframe(sql)
        tables: Series[str] = data["name"]
        tables_set: set[str] = set(tables.to_list())
        return tables_set

    def fetch_specify_sql_data(
        self, sql: str, replace_nonwords=True
    ) -> tuple[DataFrame, list[str], int]:
        """执行sql获取数据,返回如下:
        replace_noneword False 表示不自动转换列名

        data frame;
        columns;
        rows;
        """
        data: DataFrame = self.client.query_dataframe(
            sql, replace_nonwords=replace_nonwords
        )
        columns: list[str] = data.columns.to_list()
        return (data, columns, len(data))

    def convert_datatype_for_ck(self, data: DataFrame) -> DataFrame:
        """将dataframe中的数据类型转换为ck中的数据类型"""
        column_type: Series = data.dtypes
        # print(data.dtypes["class_name"])
        for column, dtype in column_type.items():
            # 将category类型转换为str
            if isinstance(dtype, CategoricalDtype):
                data[column] = data[column].astype(str)

        # print(data.dtypes["class_name"])
        return data

    def insert_specify_sql(self, sql_part: str, data: DataFrame) -> int:
        """插入ck数据
        client.insert_dataframe('INSERT INTO test VALUES', df)

        Args:
            sql_part (str): _description_
            data (DataFrame): _description_
        """
        r: int = self.client.insert_dataframe(sql_part, data)

        return r
