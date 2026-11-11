"""ClickHouse 离线测试，不访问数据库。"""

import subprocess
import sys
import unittest
from unittest.mock import patch

import clickhouse_driver
import pandas as pd
from pandas.testing import assert_frame_equal

from jwf_common_python.db_utils import ClickhouseOperator


class ClickhouseTests(unittest.TestCase):
    def setUp(self):
        client_patch = patch.object(clickhouse_driver, "Client")
        self.client_type = client_patch.start()
        self.addCleanup(client_patch.stop)
        self.operator = ClickhouseOperator(
            "localhost", port="9000", database="analytics"
        )
        self.addCleanup(self.operator.close)
        self.client = self.client_type.return_value

    def test_connection_settings_and_table_names(self):
        self.assertEqual(self.client_type.call_args.kwargs["port"], 9000)
        self.assertEqual(
            self.client_type.call_args.kwargs["settings"], {"use_numpy": True}
        )
        self.client.execute.return_value = [("events",), ("users",)]
        self.assertEqual(self.operator.fetch_all_tables(), {"events", "users"})
        self.client.query_dataframe.assert_not_called()

    def test_parameterized_dataframe_query_preserves_columns(self):
        frame = pd.DataFrame({"user-id": [1, 2]})
        self.client.query_dataframe.return_value = frame
        sql = "SELECT * FROM events WHERE name = %(name)s"
        params = {"name": "a' OR 1=1 --"}
        data, columns, count = self.operator.fetch_specify_sql_data(
            sql, replace_nonwords=False, params=params
        )
        self.assertIs(data, frame)
        self.assertEqual((columns, count), (["user-id"], 2))
        self.client.query_dataframe.assert_called_once_with(
            sql, params=params, replace_nonwords=False
        )

    def test_category_conversion_preserves_nulls_and_input(self):
        frame = pd.DataFrame(
            {
                "label": pd.Categorical(["a", None, "nan"]),
                "code": pd.Categorical([1, 2, None]),
                "mixed": pd.Categorical([1, "1", None]),
                "count": [10, 20, 30],
            }
        )
        original = frame.copy(deep=True)
        converted = self.operator.convert_datatype_for_ck(frame)
        self.assertEqual(converted["label"].tolist(), ["a", None, "nan"])
        self.assertEqual(converted["code"].tolist(), ["1", "2", None])
        self.assertEqual(converted["mixed"].tolist(), ["1", "1", None])
        self.assertEqual(converted["count"].dtype, frame["count"].dtype)
        assert_frame_equal(frame, original)
        self.assertIsNot(converted, frame)

    def test_insert_returns_row_count_and_does_not_modify_data(self):
        frame = pd.DataFrame({"id": [1, 2]})
        self.client.insert_dataframe.return_value = 2
        count = self.operator.insert_specify_sql("INSERT INTO events VALUES", frame)
        self.assertEqual(count, 2)
        self.client.insert_dataframe.assert_called_once_with(
            "INSERT INTO events VALUES", frame
        )

    def test_errors_propagate_and_context_releases_connection(self):
        error = RuntimeError("query failed")
        self.client.execute.side_effect = error
        with self.assertRaises(RuntimeError) as caught:
            with self.operator:
                self.operator.execute("SELECT 1")
        self.assertIs(caught.exception, error)
        self.operator.close()
        self.client.disconnect.assert_called_once()
        with self.assertRaises(RuntimeError):
            self.operator.fetch_all_tables()

    def test_validation_and_empty_dataframe(self):
        for kwargs in ({"host": ""}, {"port": 0}, {"port": 65536}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                ClickhouseOperator(**{"host": "localhost", **kwargs})
        with self.assertRaises(TypeError):
            self.operator.convert_datatype_for_ck([])
        with self.assertRaises(TypeError):
            self.operator.insert_specify_sql("INSERT INTO t VALUES", [])
        frame = pd.DataFrame({"label": pd.Series([], dtype="category")})
        result = self.operator.convert_datatype_for_ck(frame)
        self.assertTrue(result.empty)
        self.assertEqual(result.columns.tolist(), ["label"])

    def test_raw_sql_can_run_without_pandas_or_numpy(self):
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import sys; sys.modules['pandas'] = None; sys.modules['numpy'] = None; "
                    "from jwf_common_python.db_utils import ClickhouseOperator; "
                    "op = ClickhouseOperator('localhost', settings={'use_numpy': False}); "
                    "op.close()"
                ),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
