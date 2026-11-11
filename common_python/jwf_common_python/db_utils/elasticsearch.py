"""通用 Elasticsearch 工具，不依赖 Django 或业务模型。"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


class ElasticsearchHandle:
    def __init__(self, hosts, index: str, **client_options) -> None:
        """显式传入 hosts、索引名；认证、TLS、超时通过 client_options 传入。"""
        if not hosts:
            raise ValueError("hosts 不能为空")
        if not isinstance(index, str) or not index.strip():
            raise ValueError("index 不能为空")
        try:
            from elasticsearch import Elasticsearch
        except ImportError as exc:
            raise ImportError(
                "请先安装 Elasticsearch 依赖：pip install elasticsearch"
            ) from exc

        self.index = index
        self._closed = False
        self.elasticsearch = Elasticsearch(
            hosts=hosts, **{"request_timeout": 30, **client_options}
        )

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("Elasticsearch 客户端已关闭")

    @staticmethod
    def _document(content: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(content, Mapping):
            raise TypeError("文档内容必须为 Mapping")
        return dict(content)

    @staticmethod
    def _validate_id(doc_id) -> None:
        if (
            isinstance(doc_id, bool)
            or not isinstance(doc_id, (str, int))
            or (isinstance(doc_id, str) and not doc_id.strip())
        ):
            raise ValueError("doc_id 必须为非空字符串或整数")

    @staticmethod
    def _validate_bulk_options(id_field: str, chunk_size: int) -> None:
        if not isinstance(id_field, str) or not id_field.strip():
            raise ValueError("id_field 不能为空")
        if not isinstance(chunk_size, int) or chunk_size <= 0:
            raise ValueError("chunk_size 必须为正整数")

    def create_index(self, *, mappings=None, settings=None) -> dict[str, Any]:
        """创建索引并返回完整响应体；索引已存在时保留 SDK 的冲突异常。"""
        self._ensure_open()
        body = self.elasticsearch.indices.create(
            index=self.index, mappings=mappings, settings=settings
        ).body
        if not body.get("acknowledged"):
            raise RuntimeError("Elasticsearch 未确认索引创建")
        return body

    def init_data(
        self,
        documents: Iterable[Mapping[str, Any]],
        *,
        mappings=None,
        settings=None,
        id_field: str = "id",
        chunk_size: int = 500,
        refresh: bool | str = False,
    ) -> dict[str, Any]:
        """索引不存在时创建，然后批量创建传入文档，不查询任何业务数据库。

        已存在的文档 ID 会引发冲突，不覆盖原文档。批量导入不是事务，
        失败前已成功写入的文档不会回滚。
        """
        self._ensure_open()
        self._validate_bulk_options(id_field, chunk_size)
        index_response = None
        if not self.elasticsearch.indices.exists(index=self.index):
            index_response = self.create_index(mappings=mappings, settings=settings)
        count, errors = self.bulk_create(
            documents, id_field=id_field, chunk_size=chunk_size, refresh=refresh
        )
        return {
            "index_response": index_response,
            "success_count": count,
            "errors": errors,
        }

    def bulk_create(
        self,
        documents: Iterable[Mapping[str, Any]],
        *,
        id_field: str = "id",
        chunk_size: int = 500,
        refresh: bool | str = False,
    ) -> tuple[int, list[dict[str, Any]]]:
        """分批消费可迭代文档，返回 (成功数, 错误列表)；SDK 失败时抛异常。"""
        self._ensure_open()
        self._validate_bulk_options(id_field, chunk_size)
        from elasticsearch.helpers import bulk

        def actions():
            for record in documents:
                document = self._document(record)
                doc_id = document.get(id_field)
                self._validate_id(doc_id)
                yield {
                    "_op_type": "create",
                    "_index": self.index,
                    "_id": doc_id,
                    "_source": document,
                }

        return bulk(
            self.elasticsearch,
            actions(),
            chunk_size=chunk_size,
            raise_on_error=True,
            raise_on_exception=True,
            refresh=refresh,
        )

    def create_data(
        self, doc_id, content: Mapping[str, Any], **options
    ) -> dict[str, Any]:
        self._ensure_open()
        self._validate_id(doc_id)
        return self.elasticsearch.create(
            index=self.index, id=doc_id, document=self._document(content), **options
        ).body

    def update_data(
        self, doc_id, content: Mapping[str, Any], **options
    ) -> dict[str, Any]:
        """content 为待更新字段字典，不需要再包一层 doc。"""
        self._ensure_open()
        self._validate_id(doc_id)
        return self.elasticsearch.update(
            index=self.index, id=doc_id, doc=self._document(content), **options
        ).body

    def delete_doc(self, doc_id, **options) -> dict[str, Any]:
        self._ensure_open()
        self._validate_id(doc_id)
        return self.elasticsearch.delete(index=self.index, id=doc_id, **options).body

    def search(
        self, query: Mapping[str, Any] | None = None, **options
    ) -> dict[str, Any]:
        """执行查询并返回完整响应体，支持 size、from_、sort 等 SDK 参数。"""
        self._ensure_open()
        return self.elasticsearch.search(
            index=self.index,
            query={"match_all": {}} if query is None else self._document(query),
            **options,
        ).body

    def search_doc(
        self, key: str, *, field: str = "content", size: int = 10, offset: int = 0
    ) -> dict[str, Any]:
        """全文匹配指定字段并返回结果，包含高亮、总数等原始字段。"""
        if not isinstance(key, str) or not key.strip():
            raise ValueError("key 不能为空")
        if not isinstance(field, str) or not field.strip():
            raise ValueError("field 不能为空")
        if size <= 0 or offset < 0:
            raise ValueError("size 必须大于 0，offset 不能小于 0")
        return self.search(
            {"match": {field: key}},
            highlight={"fields": {field: {}}},
            size=size,
            from_=offset,
        )

    def show_info(self) -> dict[str, Any]:
        """保留旧接口：返回索引默认搜索页，不代表遍历所有文档。"""
        return self.search()

    def close(self) -> None:
        if not self._closed:
            try:
                self.elasticsearch.close()
            finally:
                self._closed = True

    def __enter__(self):
        self._ensure_open()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
