"""下载服务的统一返回契约；上层无需识别服务来源。"""

from typing import TypedDict

from jwf_common_python.parse_subtitle.types import SubtitleItem


class YoutubeSubtitleResult(TypedDict):
    """成功时返回非空字幕列表，按开始时间升序排列，时间单位为秒。

    language 是用于展示的语言名称，允许服务提供不同的描述；
    判断语言应使用 language_code，判断自动字幕应使用 is_generated。
    """

    video_id: str  # YouTube 视频 ID，不是完整 URL。
    language: str  # 上游提供的语言展示名称。
    language_code: str  # 标准语言码（如 en、en-US），不含 TikOmni 的 a. 前缀。
    is_generated: bool  # True 表示自动生成字幕，与语言码独立。
    subtitles: list[SubtitleItem]  # 每项包含 text、start、duration，不包含原始 SRT。
