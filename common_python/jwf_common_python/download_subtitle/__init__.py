"""字幕下载工具；YouTube 原生方案需额外安装 jwf-common-python[youtube]。"""

from typing import Any

from .tikomni import TikomniSubtitleDownloader
from .tikomni import download_youtube_subtitle as download_tikomni_subtitle
from .types import SubtitleItem, YoutubeSubtitleResult

__all__ = [
    "DEFAULT_LANGUAGES",
    "SubtitleItem",
    "YoutubeSubtitleResult",
    "download_youtube_subtitle",
    "TikomniSubtitleDownloader",
    "download_tikomni_subtitle",
]


def __getattr__(name: str) -> Any:
    # 延迟加载可选依赖，单独使用 TikOmni 时不导入 youtube_transcript_api。
    if name in {"DEFAULT_LANGUAGES", "download_youtube_subtitle"}:
        from . import youtube

        return getattr(youtube, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
