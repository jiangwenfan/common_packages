from urllib.parse import quote_plus

try:
    import pandas as pd
    import pymysql  # noqa
    from sqlalchemy import create_engine
except ImportError as exc:
    raise ImportError(
        "Couldn't import pandas sqlalchemy. \
            pip install --upgrade pandas sqlalchemy pymysql"
    ) from exc
from pandas import DataFrame, Series


class MysqlOperator:
    def __init__(self, **kwargs) -> None:
        if not {"host", "port", "user", "password", "database"}.issubset(kwargs.keys()):
            raise ValueError("host,port,user,password,database 必须提供")
        self.host = kwargs["host"]
        self.port = kwargs["port"]
        self.user = kwargs["user"]
        self.password = quote_plus(kwargs["password"])
        self.database = kwargs["database"]
        _ = f"{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        c = f"mysql+pymysql://{_}"
        self.engine = create_engine(c)

    def fetch_all_tables(self) -> set[str]:
        """获取数据库中所有的表名"""
        sql_query = """SELECT table_name AS tables FROM information_schema.tables
                        WHERE table_schema = DATABASE();
                    """
        df: DataFrame = pd.read_sql(sql_query, self.engine)
        names: Series[str] = df["tables"]
        names_set: set[str] = set(names.to_list())
        return names_set

    def fetch_specify_sql_data(self, sql: str) -> tuple[DataFrame, list[str]]:
        """执行`指定插叙sql`,获取DataFrame类型的插叙结果

        返回如下: 结果dataframe, 列名组成list

        replace_noneword False 表示不自动转换列名
        """

        data: DataFrame = pd.read_sql(sql, self.engine)
        columns: list[str] = data.columns.to_list()
        # print(type(data), columns, len(data))
        return (data, columns)

    # def execute_sql(self, sql: str, parameters) -> None:
    #     """执行sql"""
    #     with self.engine.connect() as connection:
    #         connection.execute(sql, parameters)

    # def delete_auto_increment_column(self, df: DataFrame, pk: str = "id") -> DataFrame:
    #     """删除dataframe中的自增列"""
    #     df = df.drop(columns=pk)
    #     return df

    def insert_database_mysql(self, df: DataFrame, table_name: str) -> int:
        """将dataframe中的数据插入到mysql中"""
        row: int = df.to_sql(table_name, self.engine, if_exists="append", index=False)
        return row
