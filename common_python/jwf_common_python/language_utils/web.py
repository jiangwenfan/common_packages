"""网页取词，等待全部任务结束后按 URL 输入顺序返回结果。"""

from __future__ import annotations

import math
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser

import requests

from .core import _clean_words, extract_words, filter_words, parse_urls


class _TextParser(HTMLParser):
    HIDDEN_TAGS = {"script", "style", "noscript", "template"}
    BLOCK_TAGS = {
        "p",
        "div",
        "br",
        "hr",
        "li",
        "ul",
        "ol",
        "section",
        "article",
        "header",
        "footer",
        "main",
        "nav",
        "pre",
        "blockquote",
        "table",
        "tr",
        "td",
        "th",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.chunks = []
        self.hidden_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.HIDDEN_TAGS:
            self.hidden_depth += 1
        elif not self.hidden_depth and tag in self.BLOCK_TAGS:
            self.chunks.append("\n")

    def handle_endtag(self, tag):
        if tag in self.HIDDEN_TAGS and self.hidden_depth:
            self.hidden_depth -= 1
        elif not self.hidden_depth and tag in self.BLOCK_TAGS:
            self.chunks.append("\n")

    def handle_data(self, data):
        if not self.hidden_depth:
            self.chunks.append(data)


def fetch_words_from_pages(
    urls: str | Iterable[str],
    *,
    max_workers: int = 3,
    timeout: float = 30,
    exclude_words: Iterable[str] = (),
    known_words: Iterable[str] = (),
    min_length: int = 2,
    unique: bool = True,
    case_sensitive: bool = False,
) -> dict[str, list[str]]:
    """获取 HTML 中的英文片段，移除标签及 script/style/noscript/template 内容。

    不执行 JavaScript；结果不代表已通过词典校验。默认过滤单字母并去重，
    不更改输入拼写。任何 HTTP/网络错误直接抛出，不返回不完整的成功结果。
    """
    if (
        isinstance(max_workers, bool)
        or not isinstance(max_workers, int)
        or max_workers <= 0
    ):
        raise ValueError("max_workers 必须为正整数")
    if (
        isinstance(timeout, bool)
        or not isinstance(timeout, (int, float))
        or not math.isfinite(timeout)
        or timeout <= 0
    ):
        raise ValueError("timeout 必须为有限的正数")
    targets = parse_urls(urls)
    excluded = tuple(_clean_words(exclude_words))
    known = tuple(_clean_words(known_words))
    options = dict(
        exclude_words=excluded,
        known_words=known,
        min_length=min_length,
        unique=unique,
        case_sensitive=case_sensitive,
    )
    filter_words([], **options)  # 在发起网络请求前检查取词参数。

    def fetch(url):
        with requests.get(url, timeout=timeout) as response:
            response.raise_for_status()
            parser = _TextParser()
            parser.feed(response.text)
            parser.close()
        return extract_words("".join(parser.chunks), **options)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return dict(zip(targets, executor.map(fetch, targets)))
