"""Azure TTS 离线测试：HTTP 调用全部 mock。"""

from unittest.mock import Mock, patch
from xml.etree import ElementTree

import pytest
from requests import HTTPError, Timeout

from jwf_common_python.tts.azure import TTSMicrosoft


def test_fetch_access_token() -> None:
    tts = TTSMicrosoft("test-key", "eastasia", timeout=5)
    with patch("jwf_common_python.tts.azure.microsoft.requests.post") as post:
        post.return_value.text = "offline-token"
        assert tts.fetch_access_token() == "offline-token"
        post.return_value.raise_for_status.assert_called_once_with()
    post.assert_called_once_with(
        "https://eastasia.api.cognitive.microsoft.com/sts/v1.0/issueToken",
        headers={"Ocp-Apim-Subscription-Key": "test-key"}, timeout=5,
    )


@pytest.mark.parametrize("language,code", [("en", "en-US"), ("zh", "zh-CN")])
def test_generate_xml_data(language: str, code: str) -> None:
    tts = TTSMicrosoft("test-key", "eastasia", language=language)
    root = ElementTree.fromstring(tts.generate_xml_data("你好 & <world>"))
    voice = root.find("voice")
    assert root.attrib["{http://www.w3.org/XML/1998/namespace}lang"] == code
    assert voice is not None and voice.text == "你好 & <world>"
    assert voice.attrib["name"] == tts.name


def test_convert_text_to_speech(capsys: pytest.CaptureFixture[str]) -> None:
    tts = TTSMicrosoft("test-key", "eastasia", language="zh")
    token = Mock(text="offline-token")
    audio = Mock(content=b"RIFF\x00\x00\x00\x00WAVE")
    with patch("jwf_common_python.tts.azure.microsoft.requests.post") as post:
        post.side_effect = [token, audio]
        assert tts.convert_text_to_speech("你好") == audio.content
    assert post.call_count == 2
    request = post.call_args
    assert request.args == (tts.txt_to_speech_url,)
    assert request.kwargs["headers"]["Authorization"] == "Bearer offline-token"
    assert request.kwargs["headers"]["X-Microsoft-OutputFormat"] == tts.output_format
    assert request.kwargs["data"] == tts.generate_xml_data("你好").encode("utf-8")
    assert request.kwargs["timeout"] == 30
    audio.raise_for_status.assert_called_once_with()
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("operation", ["fetch_access_token", "convert_text_to_speech"])
def test_http_errors_are_propagated(operation: str) -> None:
    tts = TTSMicrosoft("test-key", "eastasia")
    response = Mock()
    response.raise_for_status.side_effect = HTTPError("unauthorized")
    with patch(
        "jwf_common_python.tts.azure.microsoft.requests.post", return_value=response
    ):
        with pytest.raises(HTTPError, match="unauthorized"):
            if operation == "fetch_access_token":
                tts.fetch_access_token()
            else:
                tts.convert_text_to_speech("hello")


def test_synthesis_http_error_is_propagated() -> None:
    tts = TTSMicrosoft("test-key", "eastasia")
    response = Mock()
    response.raise_for_status.side_effect = HTTPError("synthesis failed")
    with patch.object(tts, "fetch_access_token", return_value="offline-token"):
        with patch(
            "jwf_common_python.tts.azure.microsoft.requests.post", return_value=response
        ):
            with pytest.raises(HTTPError, match="synthesis failed"):
                tts.convert_text_to_speech("hello")


def test_timeout_is_propagated() -> None:
    tts = TTSMicrosoft("test-key", "eastasia")
    with patch(
        "jwf_common_python.tts.azure.microsoft.requests.post", side_effect=Timeout
    ):
        with pytest.raises(Timeout):
            tts.convert_text_to_speech("hello")
