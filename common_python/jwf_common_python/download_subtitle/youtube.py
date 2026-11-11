"""YouTube 字幕下载，配置由调用方传入，不依赖 Django。"""

import logging
from collections.abc import Mapping, Sequence

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import GenericProxyConfig

from .result import build_subtitle_result
from .types import YoutubeSubtitleResult

DEFAULT_LANGUAGES: tuple[str, ...] = ("en",)
logger = logging.getLogger(__name__)


def _build_proxy_config(
    config: Mapping[str, str | None] | None,
) -> GenericProxyConfig | None:
    """空配置直连；支持仅配置 HTTP 或 HTTPS 代理。"""
    config = config or {}
    http_url = config.get("http_url") or None
    https_url = config.get("https_url") or None
    if not http_url and not https_url:
        return None
    return GenericProxyConfig(http_url=http_url, https_url=https_url)


def download_youtube_subtitle(
    video_id: str,
    *,
    languages: Sequence[str] = DEFAULT_LANGUAGES,
    proxy_config: Mapping[str, str | None] | None = None,
) -> YoutubeSubtitleResult:
    """按语言优先级下载，默认英文；返回统一结果，空字幕报 ValueError。

    上游请求异常原样传递；正文保留换行，时间统一为浮点秒数。
    """
    proxy = _build_proxy_config(proxy_config)
    logger.info(
        "下载 YouTube 字幕 video_id=%s: %s",
        video_id,
        "使用代理下载" if proxy else "未配置代理, 直连下载",
    )
    transcript = YouTubeTranscriptApi(proxy_config=proxy).fetch(
        video_id, languages=list(languages)
    )
    # 适配器只负责取得字幕，共同的构造入口保证两种来源的结果契约一致。
    return build_subtitle_result(
        video_id=transcript.video_id,
        language=transcript.language,
        language_code=transcript.language_code,
        is_generated=transcript.is_generated,
        subtitles=transcript.to_raw_data(),
    )
