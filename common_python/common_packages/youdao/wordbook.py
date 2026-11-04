"""有道单词本工具；不读写文件，不打印，不在导入时发起请求。"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import requests

WORDBOOK_URL = "https://youdao.com/wordbook/webapi/words"


def fetch_wordbook_data(
    cookie: str,
    limit: int = 15,
    offset: int = 0,
    timeout: float = 30,
) -> dict[str, Any]:
    """获取一页单词本，返回完整 JSON，保留所有响应字段。

    cookie 为浏览器请求头中的完整 Cookie 字符串。
    HTTP 错误、超时、JSON 解析失败直接抛出 requests 对应异常；
    接口返回失败状态时抛出 ValueError。
    """
    if not cookie.strip():
        raise ValueError("cookie 不能为空")
    if limit <= 0:
        raise ValueError("limit 必须大于 0")
    if offset < 0:
        raise ValueError("offset 不能小于 0")

    response = requests.get(
        WORDBOOK_URL,
        params={"limit": limit, "offset": offset},
        headers={"Cookie": cookie},
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict) or data.get("msg") != "SUCCESS":
        raise ValueError("获取有道单词本失败，请检查登录状态和 Cookie")
    return data


def fetch_all_wordbook_data(
    cookie: str, limit: int = 15, timeout: float = 30
) -> list[dict[str, Any]]:
    """按页导出整个单词本，返回每页完整 JSON 响应组成的列表。

    单词及释义等原始字段位于每页的 data.itemList 中，不提取或删减字段。
    中途请求失败时抛出异常，不将部分结果当作完整导出返回。
    """
    pages = []
    offset = 0
    while True:
        page = fetch_wordbook_data(cookie, limit=limit, offset=offset, timeout=timeout)
        data = page.get("data")
        if not isinstance(data, dict) or not isinstance(data.get("itemList"), list):
            raise ValueError("有道单词本响应缺少 data.itemList")
        total = data.get("total")
        if not isinstance(total, int) or total < 0:
            raise ValueError("有道单词本响应中的 total 无效")

        pages.append(page)
        items = data["itemList"]
        offset += len(items)
        if not items and offset < total:
            raise ValueError("有道单词本尚未导出完毕，但接口返回了空页")
        if offset >= total:
            return pages


def filter_new_words(
    existing_words: Iterable[str], current_words: Iterable[str]
) -> list[str]:
    """返回当前词表中尚未存在的单词，按当前顺序去重。

    两个参数均为单词字符串的可迭代对象；多行文本请先调用 splitlines()。
    去除首尾空白、忽略空词，保留大小写差异，不修改传入的词表。
    """
    seen = {word.strip() for word in existing_words}
    new_words = []
    for word in current_words:
        word = word.strip()
        if word and word not in seen:
            seen.add(word)
            new_words.append(word)
    return new_words
