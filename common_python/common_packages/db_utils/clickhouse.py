"""ClickHouse 查询和 DataFrame 写入工具。"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pandas import DataFrame


def _pandas():
    try:
        import pandas
    except ImportError as exc:
        raise ImportError("DataFrame 功能需要：pip install pandas numpy") from exc
    return pandas


class ClickhouseOperator:
    def __init__(
        self,
        host: str,
        port: int | str = 9000,
        user: str = "default",
        password: str = "",
        database: str = "default",
        *,
        settings: dict[str, Any] | None = None,
        **client_options,
    ) -> None:
        """使用原生 TCP 协议，client_options 可配置 TLS、连接超时等。

        默认启用 NumPy，与原 DataFrame 写入行为一致。
        仅执行普通 SQL 时可传 settings={"use_numpy": False}，无需 NumPy/pandas。
        """
        if not isinstance(host, str) or not host.strip():
            raise ValueError("host 不能为空")
        port = int(port)
        if not 1 <= port <= 65535:
            raise ValueError("port 必须在 1 到 65535 之间")
        try:
            from clickhouse_driver import Client
        except ImportError as exc:
            raise ImportError(
                "请先安装 ClickHouse 依赖：pip install clickhouse-driver numpy"
            ) from exc

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self._closed = False
        self.client = Client(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            settings={"use_numpy": True, **(settings or {})},
            **client_options,
        )

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("ClickHouse 客户端已关闭")

    def execute(self, sql: str, params=None, **options):
        """执行 SQL 并返回原始结果，params 交由驱动绑定，不拼接参数。"""
        self._ensure_open()
        return self.client.execute(sql, params=params, **options)

    def fetch_all_tables(self) -> set[str]:
        """返回当前数据库的表名，无需创建 DataFrame。"""
        return {row[0] for row in self.execute("SHOW TABLES")}

    def fetch_specify_sql_data(
        self, sql: str, replace_nonwords: bool = True, *, params=None, **options
    ) -> tuple[DataFrame, list[str], int]:
        """返回 (DataFrame, 列名, 行数)，保留旧接口并增加查询参数绑定。"""
        self._ensure_open()
        _pandas()
        data = self.client.query_dataframe(
            sql, params=params, replace_nonwords=replace_nonwords, **options
        )
        return data, data.columns.to_list(), len(data)

    @staticmethod
    def convert_datatype_for_ck(data: DataFrame) -> DataFrame:
        """复制后将 category 列转为字符串，缺失值保留为 None，不修改原数据。"""
        pd = _pandas()
        if not isinstance(data, pd.DataFrame):
            raise TypeError("data 必须为 pandas.DataFrame")
        result = data.copy(deep=True)
        for column, dtype in result.dtypes.items():
            if isinstance(dtype, pd.CategoricalDtype):
                values = result[column].astype(object).map(str, na_action="ignore")
                result[column] = values.where(values.notna(), None)
        return result

    def insert_specify_sql(self, sql_part: str, data: DataFrame, **options) -> int:
        """按指定 INSERT SQL 写入 DataFrame，返回驱动报告的写入行数。

        不自动转换数据；需要转换 category 时先调用 convert_datatype_for_ck。
        """
        self._ensure_open()
        pd = _pandas()
        if not isinstance(data, pd.DataFrame):
            raise TypeError("data 必须为 pandas.DataFrame")
        return self.client.insert_dataframe(sql_part, data, **options)

    def close(self) -> None:
        if not self._closed:
            try:
                self.client.disconnect()
            finally:
                self._closed = True

    def __enter__(self):
        self._ensure_open()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
