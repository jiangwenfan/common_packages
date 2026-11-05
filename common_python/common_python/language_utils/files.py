"""只在显式调用时读取指定路径，不创建目录或写文件。"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from .core import extract_words, filter_words, parse_urls


def read_words(path: str | Path, *, encoding: str = "utf-8", **options) -> list[str]:
    """读取指定文本文件并取词，options 同 extract_words。"""
    return extract_words(Path(path).read_text(encoding=encoding), **options)


def read_word_lists(
    paths: Iterable[str | Path],
    *,
    encoding: str = "utf-8",
    case_sensitive: bool = False,
) -> list[str]:
    """合并多个词表文件并去重，保留首次出现拼写，修复旧代码只保留最后文件的问题。"""
    if isinstance(paths, (str, Path)):
        raise TypeError("paths 必须为路径的可迭代对象，例如 [path]")
    words = (word for path in paths for word in read_words(path, encoding=encoding))
    return filter_words(words, unique=True, case_sensitive=case_sensitive)


def read_urls(path: str | Path, *, encoding: str = "utf-8") -> list[str]:
    return parse_urls(Path(path).read_text(encoding=encoding))


def generate_file_menu(
    directory: str | Path, *, prefix: str = "", recursive: bool = True
) -> tuple[list[str], str]:
    """列出 .txt 文件，返回排序后的相对路径列表及换行连接的菜单文本。

    prefix 筛选首级文件或目录名，例如旧数据的 wanglu_ 前缀。
    相对子路径保留，避免不同目录下的同名文件混淆。
    """
    root = Path(directory)
    if not root.exists():
        raise FileNotFoundError(root)
    if not root.is_dir():
        raise NotADirectoryError(root)
    candidates = root.rglob("*.txt") if recursive else root.glob("*.txt")
    paths = sorted(
        path.relative_to(root).as_posix()
        for path in candidates
        if path.is_file() and path.relative_to(root).parts[0].startswith(prefix)
    )
    return paths, "\n".join(paths)
