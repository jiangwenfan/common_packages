"""欧路 OpenAPI 生词本客户端，不打印、不读写文件、不退出进程。"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from typing import Any

import requests

BASE_URL = "https://api.frdic.com/api/open/v1/studylist"
MAX_PAGE = 50


class _TokenAuth(requests.auth.AuthBase):
    def __init__(self, token: str) -> None:
        self._token = token

    def __call__(self, request):
        request.headers["Authorization"] = self._token
        return request


class EudicClient:
    def __init__(
        self, token: str, *, language: str = "en", timeout: float = 30
    ) -> None:
        """token 为完整 Authorization 请求头值，例如 NIS 开头的授权字符串。"""
        if not isinstance(token, str) or not token.strip():
            raise ValueError("token 不能为空")
        if language not in ("en", "fr", "de", "es"):
            raise ValueError("language 必须为 en、fr、de 或 es")
        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError("timeout 必须为有限的正数")
        self.language = language
        self.timeout = timeout
        self._closed = False
        self._session = requests.Session()
        # 显式认证，避免 .netrc 中的 BasicAuth 覆盖传入 Token。
        self._session.auth = _TokenAuth(token)
        self._session.headers["Content-Type"] = "application/json"

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("欧路客户端已关闭")

    @staticmethod
    def _validate_book_id(book_id: str | int) -> None:
        if (
            isinstance(book_id, bool)
            or not isinstance(book_id, (str, int))
            or (isinstance(book_id, str) and not book_id.strip())
            or (isinstance(book_id, int) and book_id < 0)
        ):
            raise ValueError("book_id 必须为非空字符串或非负整数，0 表示默认生词本")

    def _request(
        self, method: str, path: str, *, expected_status: int, **kwargs
    ) -> dict[str, Any]:
        self._ensure_open()
        with self._session.request(
            method,
            f"{BASE_URL}/{path}",
            timeout=self.timeout,
            allow_redirects=False,
            **kwargs,
        ) as response:
            response.raise_for_status()
            if response.status_code != expected_status:
                raise requests.HTTPError(
                    f"欧路接口返回非预期状态码 {response.status_code}，预期 {expected_status}",
                    response=response,
                )
            body = response.json()
        if not isinstance(body, dict):
            raise ValueError("欧路接口响应必须为 JSON 对象")
        return body

    def create_book(self, name: str) -> dict[str, Any]:
        """创建指定名称的生词本，返回完整响应；ID 位于 data.id。"""
        self._ensure_open()
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name 不能为空")
        body = self._request(
            "POST",
            "category",
            expected_status=201,
            json={"language": self.language, "name": name},
        )
        data = body.get("data")
        if not isinstance(data, dict) or "id" not in data:
            raise ValueError("创建生词本的响应缺少 data.id")
        self._validate_book_id(data["id"])
        return body

    def list_books(self) -> dict[str, Any]:
        """返回所有生词本的完整响应，生词本列表位于 data。"""
        body = self._request(
            "GET", "category", expected_status=200, params={"language": self.language}
        )
        if not isinstance(body.get("data"), list):
            raise ValueError("生词本列表响应缺少 data 数组")
        return body

    def add_words(
        self, book_id: str | int, words: Iterable[str], *, star: int | None = None
    ) -> dict[str, Any]:
        """向指定生词本写入 1～1000 个单词，返回完整响应。

        默认保留已有单词星级，使用服务端兼容的 words 字段；传入 star=1～5
        时使用推荐的 items 字段，显式设置本批单词星级。不自动创建生词本。
        """
        self._ensure_open()
        self._validate_book_id(book_id)
        if star is not None and (
            isinstance(star, bool) or not isinstance(star, int) or not 1 <= star <= 5
        ):
            raise ValueError("star 必须为 1 到 5 的整数或 None")
        if isinstance(words, (str, bytes, Mapping)):
            raise TypeError("words 必须为单词字符串的可迭代对象")
        clean_words = []
        for word in words:
            if not isinstance(word, str) or not word.strip():
                raise ValueError("单词必须为非空字符串")
            clean_words.append(word.strip())
            if len(clean_words) > 1000:
                raise ValueError("单次最多导入 1000 个单词")
        if not clean_words:
            raise ValueError("words 不能为空")
        body = {"category_id": book_id, "language": self.language}
        if star is None:
            body["words"] = clean_words
        else:
            body["items"] = [{"word": word, "star": star} for word in clean_words]
        return self._request("POST", "words", expected_status=201, json=body)

    def get_words(
        self,
        book_id: str | int,
        *,
        page: int = 0,
        page_size: int = 100,
        sort: str = "asc",
    ) -> dict[str, Any]:
        """获取一页完整响应，页码从 0 开始；单词、释义等原始字段位于 data。"""
        self._ensure_open()
        self._validate_book_id(book_id)
        if (
            isinstance(page, bool)
            or not isinstance(page, int)
            or not 0 <= page <= MAX_PAGE
        ):
            raise ValueError(f"page 必须为 0 到 {MAX_PAGE} 的整数")
        if (
            isinstance(page_size, bool)
            or not isinstance(page_size, int)
            or not 1 <= page_size <= 100
        ):
            raise ValueError("page_size 必须为 1 到 100 的整数")
        if sort not in ("asc", "desc"):
            raise ValueError("sort 必须为 asc 或 desc")
        body = self._request(
            "GET",
            "words",
            expected_status=200,
            params={
                "category_id": book_id,
                "language": self.language,
                "page": page,
                "page_size": page_size,
                "sort": sort,
            },
        )
        if not isinstance(body.get("data"), list):
            raise ValueError("单词列表响应缺少 data 数组")
        return body

    def export_book(
        self, book_id: str | int, *, page_size: int = 100, sort: str = "asc"
    ) -> list[dict[str, Any]]:
        """从第 0 页导出，返回每页完整响应，不写文件。

        短页/空页表示导出结束。若第 50 页仍为满页，受接口上限限制无法确认
        是否完整，此时抛出 RuntimeError；请求失败也不返回部分结果冒充完整导出。
        """
        pages = []
        for page in range(MAX_PAGE + 1):
            body = self.get_words(book_id, page=page, page_size=page_size, sort=sort)
            pages.append(body)
            if len(body["data"]) < page_size:
                return pages
        raise RuntimeError("已达到欧路接口分页上限，无法确认已导出全部单词")

    def close(self) -> None:
        if not self._closed:
            try:
                self._session.close()
            finally:
                self._closed = True

    def __enter__(self):
        self._ensure_open()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
