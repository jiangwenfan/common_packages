"""将字幕内容解析为统一的数据结构。"""

from .srt import parse_srt
from .types import SubtitleItem

__all__ = ["parse_srt", "SubtitleItem"]
