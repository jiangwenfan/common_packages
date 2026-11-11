"""各下载适配器共用的结果构造逻辑，不包含任何网络调用。"""

from collections.abc import Iterable
import math

from .types import SubtitleItem, YoutubeSubtitleResult


def build_subtitle_result(
    *,
    video_id: str,
    language: str,
    language_code: str,
    is_generated: bool,
    subtitles: Iterable[SubtitleItem],
) -> YoutubeSubtitleResult:
    """复制并校验字幕、统一秒数类型和顺序；无可用字幕时抛出 ValueError。"""
    items = [_normalize_item(item) for item in subtitles]
    if not items:
        raise ValueError("该视频没有可用的字幕")
    # 稳定排序：开始时间相同的字幕保留原顺序，也不修改上游数据。
    items.sort(key=lambda item: item["start"])
    return {
        "video_id": video_id,
        "language": language,
        "language_code": language_code,
        "is_generated": is_generated,
        "subtitles": items,
    }


def _normalize_item(item: SubtitleItem) -> SubtitleItem:
    """保留正文及换行，拒绝无法用于播放定位的负数或非有限时间。"""
    start, duration = float(item["start"]), float(item["duration"])
    if not all(math.isfinite(value) and value >= 0 for value in (start, duration)):
        raise ValueError("字幕时间轴无效")
    return {"text": item["text"], "start": start, "duration": duration}
