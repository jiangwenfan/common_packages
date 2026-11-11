"""同一视频通过不同下载服务取得字幕时，应具备相同的业务字段语义。"""

from unittest.mock import Mock, patch

import pytest
from typing import Literal

from jwf_common_python.download_subtitle import tikomni, youtube
from jwf_common_python.download_subtitle.result import build_subtitle_result
from jwf_common_python.download_subtitle.types import SubtitleItem, YoutubeSubtitleResult


def _download_both(
    language_code: str, generated: bool
) -> tuple[YoutubeSubtitleResult, YoutubeSubtitleResult]:
    """模拟两种服务的不同传输格式，避免真实网络请求，并核对上游语言标识。"""
    video_id = "dQw4w9WgXcQ"
    code = f"a.{language_code}" if generated else language_code
    transcript = Mock(
        video_id=video_id,
        language="English",
        language_code=language_code,
        is_generated=generated,
    )
    transcript.to_raw_data.return_value = [
        {"text": "Second", "start": 3, "duration": 2},
        {"text": "Hello\nworld", "start": 1.25, "duration": 1.75},
    ]
    srt = "2\n00:00:03,000 --> 00:00:05,000\nSecond\n\n1\n00:00:01,250 --> 00:00:03,000\nHello\nworld\n"
    with patch.object(youtube, "YouTubeTranscriptApi") as api, patch.object(
        tikomni.TikomniSubtitleDownloader,
        "_request",
        side_effect=[{"captions": [{"language_code": code}]}, {"content": srt}],
    ) as request:
        api.return_value.fetch.return_value = transcript
        native = youtube.download_youtube_subtitle(video_id)
        other = tikomni.download_youtube_subtitle(video_id, api_token="test-token")
    assert request.call_args.args[1]["language_code"] == code
    return native, other


@pytest.mark.parametrize("language_code", ["en", "en-US"])
@pytest.mark.parametrize("generated", [False, True])
def test_providers_share_result_contract(language_code: str, generated: bool) -> None:
    """场景：人工/自动字幕使用普通/区域英文，且上游条目乱序。

    两个 mock 服务提供相同内容，但使用各自的语言标记和内容格式。
    调用两个公开下载函数后比较业务结果，预期语言码、生成标记、顺序与秒数类型一致。
    """
    native, other = _download_both(language_code, generated)
    assert native == other
    assert other["language_code"] == language_code
    assert other["is_generated"] is generated
    assert [item["text"] for item in other["subtitles"]] == ["Hello\nworld", "Second"]
    assert all(
        isinstance(item[key], float)
        for item in other["subtitles"]
        for key in ("start", "duration")
    )


@pytest.mark.parametrize("field", ["start", "duration"])
@pytest.mark.parametrize("value", [-1.0, float("nan"), float("inf")])
def test_invalid_timestamps_are_rejected(
    field: Literal["start", "duration"], value: float
) -> None:
    """场景：上游时间含负数、NaN 或无穷值；构造单条字幕并统一转换，预期拒绝无效定位数据。"""
    item: SubtitleItem = {"text": "Hello", "start": 0.0, "duration": 1.0}
    item[field] = value
    with pytest.raises(ValueError, match="时间轴"):
        build_subtitle_result(
            video_id="video",
            language="English",
            language_code="en",
            is_generated=False,
            subtitles=[item],
        )
