"""模拟第三方字幕服务，验证下载协议且不访问网络。"""

from unittest.mock import Mock, patch

import pytest
from youtube_transcript_api import TranscriptsDisabled

from jwf_common_python.download_subtitle import youtube


@pytest.fixture
def api():
    # 在客户端入口拦截调用，确保所有测试都不会真实请求 YouTube。
    with patch.object(youtube, "YouTubeTranscriptApi") as client:
        transcript = Mock(
            video_id="dQw4w9WgXcQ",
            language="English",
            language_code="en",
            is_generated=False,
        )
        transcript.to_raw_data.return_value = [
            {"text": "hello", "start": 1, "duration": "2.5"}
        ]
        client.return_value.fetch.return_value = transcript
        yield client


def test_default_download(api):
    result = youtube.download_youtube_subtitle("dQw4w9WgXcQ")
    api.assert_called_once_with(proxy_config=None)
    api.return_value.fetch.assert_called_once_with("dQw4w9WgXcQ", languages=["en"])
    # 保持原有返回结构，并将时间字段统一转换为浮点数。
    assert result == {
        "video_id": "dQw4w9WgXcQ",
        "language": "English",
        "language_code": "en",
        "is_generated": False,
        "subtitles": [{"text": "hello", "start": 1.0, "duration": 2.5}],
    }
    assert isinstance(result["subtitles"][0]["start"], float)


@pytest.mark.parametrize("config", [None, {}, {"http_url": "", "https_url": None}])
def test_empty_proxy_uses_direct_connection(api, config):
    youtube.download_youtube_subtitle("dQw4w9WgXcQ", proxy_config=config)
    api.assert_called_once_with(proxy_config=None)


@pytest.mark.parametrize("key", ["http_url", "https_url"])
def test_single_proxy_and_languages(api, key, caplog):
    url = "http://user:secret@proxy.example:8080"
    with caplog.at_level("INFO"):
        youtube.download_youtube_subtitle(
            "dQw4w9WgXcQ", proxy_config={key: url}, languages=["zh-Hans", "en"]
        )
    proxy = api.call_args.kwargs["proxy_config"]
    assert getattr(proxy, key) == url
    api.return_value.fetch.assert_called_once_with(
        "dQw4w9WgXcQ", languages=["zh-Hans", "en"]
    )
    # 代理地址可能包含凭证，日志只描述连接方式。
    assert "secret" not in caplog.text


def test_two_proxies(api):
    config = {"http_url": "http://proxy:8080", "https_url": "http://proxy:8081"}
    youtube.download_youtube_subtitle("dQw4w9WgXcQ", proxy_config=config)
    proxy = api.call_args.kwargs["proxy_config"]
    assert proxy.http_url == config["http_url"]
    assert proxy.https_url == config["https_url"]


def test_generated_empty_transcript(api):
    """场景：上游自动字幕内容为空；模拟空列表后执行下载，预期与 TikOmni 一致报错，不返回成功的空字幕。"""
    transcript = api.return_value.fetch.return_value
    transcript.is_generated = True
    transcript.to_raw_data.return_value = []
    with pytest.raises(ValueError, match="没有可用"):
        youtube.download_youtube_subtitle("dQw4w9WgXcQ")


def test_service_error_propagates(api):
    error = TranscriptsDisabled("dQw4w9WgXcQ")
    api.return_value.fetch.side_effect = error
    with pytest.raises(TranscriptsDisabled) as caught:
        youtube.download_youtube_subtitle("dQw4w9WgXcQ")
    assert caught.value is error
