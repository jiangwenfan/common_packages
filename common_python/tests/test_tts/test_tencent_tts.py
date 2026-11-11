"""使用真实公共 SDK 和 mock HTTP 传输验证 TextToVoice，不访问腾讯云。"""

import base64
import builtins
import json
from collections.abc import Iterator
from typing import Any
from unittest.mock import Mock, patch
from uuid import UUID

import pytest
from requests import Response
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)

from jwf_common_python.tts import TTSTencent

AUDIO = b"RIFF\x00\x01WAVE\x00\xff"
BODY = {
    "Audio": base64.b64encode(AUDIO).decode(),
    "SessionId": "session-1234",
    "Subtitles": [{"Text": "你好", "BeginTime": 250, "EndTime": 670}],
    "RequestId": "offline-request-id",
    "ExtraField": {"preserved": True},
}


def http_response(body: Any, status: int = 200) -> Response:
    response = Response()
    response.status_code = status
    response.headers["Content-Type"] = "application/json"
    response._content = json.dumps({"Response": body}).encode()
    return response


@pytest.fixture
def client() -> Iterator[tuple[TTSTencent, Mock]]:
    with TTSTencent("test-id", "test-key", region="ap-guangzhou", timeout=5) as tts:
        with patch.object(tts.client.request, "send_request") as send:
            send.return_value = http_response(BODY)
            yield tts, send


def test_sdk_configuration_and_signed_request(client: tuple[TTSTencent, Mock]) -> None:
    tts, send = client
    assert tts.client.region == "ap-guangzhou"
    assert tts.client.profile.httpProfile.endpoint == "tts.tencentcloudapi.com"
    assert tts.client.profile.httpProfile.reqTimeout == 5
    send.assert_not_called()
    assert tts.text_to_voice("你好", voice_type=1001) == BODY
    request = send.call_args.args[0]
    assert request.header["X-TC-Action"] == "TextToVoice"
    assert request.header["X-TC-Version"] == "2019-08-23"
    assert request.header["X-TC-Region"] == "ap-guangzhou"
    assert request.header["Authorization"].startswith("TC3-HMAC-SHA256 ")
    assert "/tts/tc3_request" in request.header["Authorization"]
    assert "X-TC-Token" not in request.header
    params = json.loads(request.data)
    assert UUID(params.pop("SessionId")).version == 4
    assert params == {
        "Text": "你好", "ModelType": 1,
        "VoiceType": 1001, "PrimaryLanguage": 1, "SampleRate": 16000,
        "Codec": "wav", "EnableSubtitle": True, "Speed": 0, "Volume": 0,
    }


def test_all_apifox_options_are_serialized(client: tuple[TTSTencent, Mock]) -> None:
    tts, send = client
    tts.text_to_voice(
        "<speak>你好</speak>", "session-1234", volume=1.5, speed=-0.25,
        project_id=123, model_type=1, voice_type=200000000,
        fast_voice_type="WCHN-test", primary_language=2, sample_rate=24000,
        codec="mp3", enable_subtitle=True, segment_rate=2,
        emotion_category="happy", emotion_intensity=150,
    )
    assert json.loads(send.call_args.args[0].data) == {
        "Text": "<speak>你好</speak>", "SessionId": "session-1234",
        "Volume": 1.5, "Speed": -0.25, "ProjectId": 123, "ModelType": 1,
        "VoiceType": 200000000, "FastVoiceType": "WCHN-test",
        "PrimaryLanguage": 2, "SampleRate": 24000, "Codec": "mp3",
        "EnableSubtitle": True, "SegmentRate": 2,
        "EmotionCategory": "happy", "EmotionIntensity": 150,
    }


@pytest.mark.parametrize("codec", ["wav", "mp3", "pcm"])
def test_audio_is_returned_as_base64(client: tuple[TTSTencent, Mock], codec: str) -> None:
    tts, send = client
    assert tts.text_to_voice("你好", voice_type=1001, codec=codec)["Audio"] == BODY["Audio"]
    assert json.loads(send.call_args.args[0].data)["Codec"] == codec


def test_unique_sessions_and_independent_options(
    client: tuple[TTSTencent, Mock],
) -> None:
    tts, send = client
    tts.text_to_voice(
        " hello ", voice_type=501000, speed=1, volume=2,
        enable_subtitle=False, codec="pcm",
    )
    first = json.loads(send.call_args.args[0].data)
    tts.text_to_voice("世界", voice_type=601013)
    second = json.loads(send.call_args.args[0].data)
    assert UUID(first["SessionId"]) != UUID(second["SessionId"])
    assert first["Text"] == " hello "
    assert second["Text"] == "世界"
    assert first["VoiceType"] == 501000 and second["VoiceType"] == 601013
    assert first["Speed"] == 1 and first["Volume"] == 2
    assert first["EnableSubtitle"] is False and first["Codec"] == "pcm"
    assert second["Speed"] == 0 and second["Volume"] == 0
    assert second["EnableSubtitle"] is True and second["Codec"] == "wav"


def test_http_200_business_error_is_raised(client: tuple[TTSTencent, Mock]) -> None:
    tts, send = client
    send.return_value = http_response({
        "Error": {"Code": "InvalidParameterValue.TextEmpty", "Message": "Text不能为空"},
        "RequestId": "failed-request-id",
    })
    with pytest.raises(TencentCloudSDKException) as error:
        tts.text_to_voice("你好", voice_type=1001)
    assert error.value.code == "InvalidParameterValue.TextEmpty"
    assert error.value.requestId == "failed-request-id"


def test_transport_failure_is_propagated(client: tuple[TTSTencent, Mock]) -> None:
    tts, send = client
    send.side_effect = TencentCloudSDKException("ClientNetworkError", "timeout")
    with pytest.raises(TencentCloudSDKException, match="ClientNetworkError"):
        tts.text_to_voice("你好", voice_type=1001)


def test_http_error_is_raised(client: tuple[TTSTencent, Mock]) -> None:
    tts, send = client
    send.return_value = http_response({}, status=503)
    with pytest.raises(TencentCloudSDKException):
        tts.text_to_voice("你好", voice_type=1001)


@pytest.mark.parametrize("body", [[], {}, {"Audio": None}, {"Audio": 123}])
def test_invalid_response_is_rejected(
    client: tuple[TTSTencent, Mock], body: Any,
) -> None:
    tts, send = client
    send.return_value = http_response(body)
    with pytest.raises(ValueError, match="Audio"):
        tts.text_to_voice("你好", voice_type=1001)


def test_sdk_response_parsing_error_is_propagated(
    client: tuple[TTSTencent, Mock],
) -> None:
    tts, send = client
    send.return_value = http_response(None)
    # SDK 在本地响应校验之前解析 Response；保留该层异常，不伪造成功结果。
    with pytest.raises(TypeError):
        tts.text_to_voice("你好", voice_type=1001)


def test_close_is_idempotent_and_prevents_calls(
    client: tuple[TTSTencent, Mock],
) -> None:
    tts, send = client
    session = Mock()
    with patch.object(tts.client.request.conn, "_session", session, create=True):
        tts.close()
        tts.close()
    session.close.assert_called_once_with()
    with pytest.raises(RuntimeError, match="已关闭"):
        tts.text_to_voice("你好", voice_type=1001)
    with pytest.raises(RuntimeError, match="已关闭"):
        tts.__enter__()
    send.assert_not_called()


def test_context_closes_after_exception(client: tuple[TTSTencent, Mock]) -> None:
    tts, _ = client
    with patch.object(tts, "close", wraps=tts.close) as close:
        with pytest.raises(RuntimeError, match="caller failed"):
            with tts:
                raise RuntimeError("caller failed")
        close.assert_called_once_with()


def test_optional_sdk_has_install_hint() -> None:
    original_import = builtins.__import__

    def without_sdk(name: str, *args: Any, **kwargs: Any) -> Any:
        if name.startswith("tencentcloud"):
            raise ImportError("SDK missing")
        return original_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=without_sdk):
        with pytest.raises(
            ImportError, match="pip install.*tencentcloud-sdk-python-common"
        ):
            TTSTencent("id", "key")
