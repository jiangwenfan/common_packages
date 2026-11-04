"""使用真实 Elasticsearch 客户端，模拟 transport 响应，无需服务端。"""

import subprocess
import sys
import unittest
from unittest.mock import patch

from elastic_transport import ApiResponseMeta, HttpHeaders, NodeConfig
from elasticsearch import ConflictError
from elasticsearch.helpers import BulkIndexError

from common_packages.db_utils import ElasticsearchHandle


def response(body, status=200):
    return (
        ApiResponseMeta(
            status=status,
            http_version="1.1",
            duration=0,
            headers=HttpHeaders({"x-elastic-product": "Elasticsearch"}),
            node=NodeConfig("http", "localhost", 9200),
        ),
        body,
    )


def bulk_result(*ids):
    return response(
        {
            "errors": False,
            "items": [
                {"create": {"_id": str(doc_id), "status": 201}} for doc_id in ids
            ],
        }
    )


class ElasticsearchTests(unittest.TestCase):
    def setUp(self):
        self.handle = ElasticsearchHandle("http://localhost:9200", "articles")
        self.addCleanup(self.handle.close)
        request_patch = patch.object(
            self.handle.elasticsearch.transport, "perform_request"
        )
        self.request = request_patch.start()
        self.addCleanup(request_patch.stop)

    def test_search_returns_full_response_with_highlights_and_paging(self):
        body = {
            "took": 3,
            "hits": {"total": {"value": 12}, "hits": []},
            "custom": "kept",
        }
        self.request.return_value = response(body)
        self.assertEqual(
            self.handle.search_doc("python", field="title", size=5, offset=10), body
        )
        payload = self.request.call_args.kwargs["body"]
        self.assertEqual(payload["query"], {"match": {"title": "python"}})
        self.assertEqual(payload["highlight"], {"fields": {"title": {}}})
        self.assertEqual((payload["size"], payload["from"]), (5, 10))

    def test_crud_returns_sdk_bodies_and_update_wraps_partial_document(self):
        for method, result in (("create_data", "created"), ("update_data", "updated")):
            self.request.return_value = response({"result": result})
            self.assertEqual(
                getattr(self.handle, method)(0, {"title": "new"}), {"result": result}
            )
            key = "doc" if method == "update_data" else "title"
            body = self.request.call_args.kwargs["body"]
            self.assertEqual(body[key], {"title": "new"} if key == "doc" else "new")
        self.request.return_value = response({"result": "deleted"})
        self.assertEqual(self.handle.delete_doc(0), {"result": "deleted"})

    def test_crud_conflict_is_not_swallowed(self):
        self.request.return_value = response(
            {
                "error": {
                    "type": "version_conflict_engine_exception",
                    "reason": "exists",
                },
                "status": 409,
            },
            status=409,
        )
        with self.assertRaises(ConflictError):
            self.handle.create_data(1, {"title": "new"})

    def test_bulk_generator_is_chunked_without_modifying_documents(self):
        records = [{"id": value, "title": str(value)} for value in range(3)]
        original = [record.copy() for record in records]
        self.request.side_effect = [bulk_result(0, 1), bulk_result(2)]
        self.assertEqual(self.handle.bulk_create(iter(records), chunk_size=2), (3, []))
        self.assertEqual(self.request.call_count, 2)
        self.assertEqual(records, original)

    def test_bulk_failure_raises_with_document_errors(self):
        self.request.return_value = response(
            {
                "errors": True,
                "items": [
                    {
                        "create": {
                            "_id": "1",
                            "status": 409,
                            "error": {
                                "type": "version_conflict_engine_exception",
                                "reason": "exists",
                            },
                        }
                    }
                ],
            }
        )
        with self.assertRaises(BulkIndexError) as caught:
            self.handle.bulk_create([{"id": 1, "title": "new"}])
        self.assertEqual(caught.exception.errors[0]["create"]["status"], 409)

    def test_init_creates_missing_index_and_imports_supplied_records(self):
        created = {
            "acknowledged": True,
            "shards_acknowledged": True,
            "index": "articles",
        }
        self.request.side_effect = [
            response({}, 404),
            response(created),
            bulk_result(1),
        ]
        result = self.handle.init_data([{"id": 1, "content": "hello"}])
        self.assertEqual(
            result, {"index_response": created, "success_count": 1, "errors": []}
        )

    def test_init_existing_index_does_not_recreate_it(self):
        self.request.side_effect = [response({}), bulk_result(1)]
        result = self.handle.init_data([{"id": 1}])
        self.assertIsNone(result["index_response"])
        self.assertEqual(self.request.call_count, 2)

    def test_unacknowledged_index_creation_fails(self):
        self.request.return_value = response({"acknowledged": False})
        with self.assertRaisesRegex(RuntimeError, "未确认"):
            self.handle.create_index()

    def test_invalid_records_and_parameters_do_not_write(self):
        for records in ([{"title": "missing id"}], [{"id": None}], ["not a document"]):
            with self.subTest(records=records), self.assertRaises(
                (TypeError, ValueError)
            ):
                self.handle.bulk_create(records)
        for doc_id in (None, "", True, []):
            with self.subTest(doc_id=doc_id), self.assertRaises(ValueError):
                self.handle.delete_doc(doc_id)
        with self.assertRaises(ValueError):
            self.handle.bulk_create([], chunk_size=0)
        with self.assertRaises(ValueError):
            self.handle.init_data([], chunk_size=0)
        with self.assertRaises(ValueError):
            self.handle.search_doc("python", size=0)
        self.request.assert_not_called()

    def test_empty_import_and_show_info(self):
        self.assertEqual(self.handle.bulk_create([]), (0, []))
        self.request.assert_not_called()
        self.request.return_value = response({"hits": {"hits": []}})
        self.assertEqual(self.handle.show_info(), {"hits": {"hits": []}})
        self.assertEqual(
            self.request.call_args.kwargs["body"]["query"], {"match_all": {}}
        )

    def test_context_closes_client_once_and_prevents_reuse(self):
        with patch.object(self.handle.elasticsearch, "close") as close:
            with self.handle:
                pass
            self.handle.close()
            close.assert_called_once()
        with self.assertRaises(RuntimeError):
            self.handle.show_info()


class DependencyTests(unittest.TestCase):
    def test_import_without_optional_or_business_dependencies(self):
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import sys; "
                    "sys.modules.update(dict.fromkeys(['elasticsearch', 'clickhouse_driver', "
                    "'numpy', 'pandas', 'django', 'article', 'sqlalchemy', 'pymysql'])); "
                    "from common_packages.db_utils import ClickhouseOperator, ElasticsearchHandle"
                ),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_missing_dependencies_give_install_instructions(self):
        with patch.dict(
            sys.modules, {"clickhouse_driver": None, "elasticsearch": None}
        ):
            from common_packages.db_utils import ClickhouseOperator

            with self.assertRaisesRegex(ImportError, "pip install clickhouse-driver"):
                ClickhouseOperator("localhost")
            with self.assertRaisesRegex(ImportError, "pip install elasticsearch"):
                ElasticsearchHandle("http://localhost:9200", "articles")


if __name__ == "__main__":
    unittest.main()
