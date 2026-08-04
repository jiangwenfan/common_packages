import logging

import pandas as pd
import pytest

logging.basicConfig(level=logging.INFO)


@pytest.mark.usefixtures("start_stop_mysql")
class TestMysqlOperator:
    def test_fetch_all_tables(self, mysql_op):
        # 实际的
        actual_tables: set[str] = mysql_op.fetch_all_tables()
        actual_tables_num = len(actual_tables)

        # 期望的
        expected_tables = {"customers", "orders"}
        excepted_tables_num = len(expected_tables)

        assert excepted_tables_num == actual_tables_num
        assert expected_tables == actual_tables

    def test_fetch_specify_sql_data(self, mysql_op, reset_default_data):
        """获取指定sql数据"""
        data, columns = mysql_op.fetch_specify_sql_data("SELECT * FROM customers")

        expected_columns = ["customer_id", "customer_name", "email"]

        assert columns == expected_columns

    def test_insert_database_mysql(self, mysql_op, reset_default_data):
        """插入数据"""
        need_insert_data = [
            {"customer_name": "test1", "email": "test1@gmail.com"},
            {"customer_name": "test2", "email": "test2@gmail.com"},
        ]
        need_insert_dataframe = pd.DataFrame(need_insert_data)
        rows: int = mysql_op.insert_database_mysql(need_insert_dataframe, "customers")
        assert rows == 2
        # 断言共5条数据。原始3条+新插入的2条
        data, _ = mysql_op.fetch_specify_sql_data("SELECT * FROM customers")
        assert len(data) == 5
