"""字幕解析与下载共用的条目类型，时间单位为秒。"""

from typing import TypedDict


class SubtitleItem(TypedDict):
    text: str
    start: float
    duration: float
