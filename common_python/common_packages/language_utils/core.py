"""纯文本和词表处理，不读写文件，不修改输入，不配置全局日志。"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Iterable, Iterator
from urllib.parse import urlsplit

WORD_PATTERN = re.compile(r"[A-Za-z]+")


def _clean_words(words: Iterable[str]) -> Iterator[str]:
    if isinstance(words, (str, bytes)):
        raise TypeError("词表必须为字符串的可迭代对象，请将多行文本先 splitlines()")
    for word in words:
        if not isinstance(word, str):
            raise TypeError("词表中的元素必须为字符串")
        word = word.strip()
        if word:
            yield word


def _text_chunks(text: str | Iterable[str]) -> Iterator[str]:
    if isinstance(text, str):
        yield text
    else:
        for chunk in text:
            if not isinstance(chunk, str):
                raise TypeError("文本内容必须为字符串")
            yield chunk


def filter_words(
    words: Iterable[str],
    *,
    exclude_words: Iterable[str] = (),
    known_words: Iterable[str] = (),
    case_sensitive: bool = False,
    min_length: int = 1,
    unique: bool = False,
) -> list[str]:
    """排除无效/已知词，保留原文拼写和顺序，默认保留重复项。

    默认以 casefold 忽略大小写比较；unique=True 按同一规则去重。
    空白词忽略，长度按去除首尾空白后的字符串计算。
    """
    if (
        isinstance(min_length, bool)
        or not isinstance(min_length, int)
        or min_length < 1
    ):
        raise ValueError("min_length 必须为正整数")
    key = (lambda word: word) if case_sensitive else str.casefold
    excluded = {
        key(word)
        for group in (exclude_words, known_words)
        for word in _clean_words(group)
    }
    seen = set()
    result = []
    for word in _clean_words(words):
        normalized = key(word)
        if (
            len(word) >= min_length
            and normalized not in excluded
            and (not unique or normalized not in seen)
        ):
            result.append(word)
            if unique:
                seen.add(normalized)
    return result


def extract_words(text: str | Iterable[str], **options) -> list[str]:
    """提取英文 A-Z/a-z 片段，保留原分词规则，再通过 filter_words 过滤。

    连字符、撇号、数字等均为分隔符，不进行词典查验或词形还原。
    """
    words = (
        match.group()
        for chunk in _text_chunks(text)
        for match in WORD_PATTERN.finditer(chunk)
    )
    return filter_words(words, **options)


def extract_chapter(
    text: str, start_title: str, end_title: str | None = None, *, occurrence: int = -1
) -> str:
    """按完整标题行提取正文，不包含标题。

    去除标题行首尾空白后匹配；默认选择最后一次出现的起始标题，跳过目录。
    结束位置为该起始标题之后的第一个结束标题；end_title=None 表示直到文末。
    occurrence 使用 Python 索引规则，缺失标题或越界时抛出 ValueError。
    """
    if not isinstance(text, str):
        raise TypeError("text 必须为字符串")
    if not isinstance(start_title, str) or not start_title.strip():
        raise ValueError("start_title 不能为空")
    if end_title is not None and (
        not isinstance(end_title, str) or not end_title.strip()
    ):
        raise ValueError("end_title 必须为非空字符串或 None")
    if isinstance(occurrence, bool) or not isinstance(occurrence, int):
        raise ValueError("occurrence 必须为整数")
    lines = text.splitlines()
    starts = [
        index for index, line in enumerate(lines) if line.strip() == start_title.strip()
    ]
    try:
        start = starts[occurrence]
    except IndexError as exc:
        raise ValueError("找不到指定次数的起始标题") from exc
    end = len(lines)
    if end_title is not None:
        end = next(
            (
                index
                for index in range(start + 1, len(lines))
                if lines[index].strip() == end_title.strip()
            ),
            -1,
        )
        if end == -1:
            raise ValueError("起始标题之后找不到结束标题")
    return "\n".join(lines[start + 1 : end])


def get_chapter_words(
    text: str,
    start_title: str,
    end_title: str | None = None,
    *,
    occurrence: int = -1,
    **options,
) -> list[str]:
    return extract_words(
        extract_chapter(text, start_title, end_title, occurrence=occurrence), **options
    )


def word_frequencies(
    words: Iterable[str], *, top_n: int | None = None, case_sensitive: bool = False
) -> list[tuple[str, int]]:
    """按词频降序返回 (词, 次数)，同频按首次出现顺序；默认合并大小写。

    合并大小写时返回 casefold 后的词形。top_n=None 表示全部，0 返回空列表。
    """
    if top_n is not None and (
        isinstance(top_n, bool) or not isinstance(top_n, int) or top_n < 0
    ):
        raise ValueError("top_n 必须为非负整数或 None")
    cleaned = _clean_words(words)
    return Counter(
        word if case_sensitive else word.casefold() for word in cleaned
    ).most_common(top_n)


def format_words(words: Iterable[str], **options) -> str:
    """按词频排序并返回去重后的逐行词表文本，替代旧写文件函数。"""
    return "\n".join(word for word, _ in word_frequencies(words, **options))


def group_words_by_length(words: Iterable[str]) -> dict[int, list[str]]:
    """按长度分组，保留各组输入顺序和重复项。"""
    groups = {}
    for word in _clean_words(words):
        groups.setdefault(len(word), []).append(word)
    return groups


def sort_words_by_length(words: Iterable[str], *, descending: bool = True) -> list[str]:
    """按长度稳定排序，保留同长度的原顺序，不修改输入。"""
    return sorted(_clean_words(words), key=len, reverse=descending)


def is_title_case_word(word: str) -> bool:
    """保留旧判断规则：Dog 为 True，A、DOG、DoG 和带标点的文本为 False。"""
    return isinstance(word, str) and re.fullmatch(r"[A-Z][a-z]+", word) is not None


def parse_urls(text: str | Iterable[str]) -> list[str]:
    """逐行读取 HTTP(S) URL，忽略空行和 # 注释，按首次出现顺序去重。"""
    result = []
    seen = set()
    for chunk in _text_chunks(text):
        for line in chunk.splitlines():
            url = line.strip()
            if not url or url.startswith("#"):
                continue
            parts = urlsplit(url)
            _ = parts.port  # 触发端口格式及范围校验。
            if (
                parts.scheme not in ("http", "https")
                or not parts.hostname
                or any(char.isspace() for char in url)
            ):
                raise ValueError(f"无效的 HTTP(S) URL：{url}")
            if url not in seen:
                seen.add(url)
                result.append(url)
    return result
