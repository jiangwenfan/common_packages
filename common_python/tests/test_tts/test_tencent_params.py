"""参数错误在发送前被拒绝；参数边界来自 Apifox 接口定义。"""

from typing import Any
from unittest.mock import Mock, patch

import pytest

from jwf_common_python.tts import TTSTencent
from jwf_common_python.tts.tencent._tencent_params import build_params
from jwf_common_python.tts.tencent.tts import tts as voice_data


def test_get_voices_returns_local_data_without_creating_sdk() -> None:
    with patch("jwf_common_python.tts.tencent.tencent._create_client") as create:
        voices = TTSTencent.get_voices()
        assert voices == voice_data
        create.assert_not_called()


def test_get_voices_does_not_expose_mutable_source_data() -> None:
    voices = TTSTencent.get_voices()
    voices[0]["name"] = "changed"
    voices[0]["languages"].append("changed")
    voices.clear()
    assert TTSTencent.get_voices() == voice_data
    assert voice_data[0]["name"] == "智斌"
    assert voice_data[0]["languages"] == ["中文", "英文"]


@pytest.mark.parametrize("text", ["", " \n", None, 123])
def test_invalid_text_does_not_call_sdk(text: Any) -> None:
    with patch("jwf_common_python.tts.tencent.tencent._create_client") as create:
        with TTSTencent("id", "key") as tts:
            with pytest.raises(ValueError, match="text"):
                tts.text_to_voice(text, voice_type=1001)
        create.return_value.call_json.assert_not_called()


@pytest.mark.parametrize("session_id", ["", " ", 123])
def test_explicit_invalid_session_is_not_replaced(session_id: Any) -> None:
    with pytest.raises(ValueError, match="session_id"):
        build_params("你好", 1001, session_id, {})


def test_voice_type_is_required_before_sending_request() -> None:
    with patch("jwf_common_python.tts.tencent.tencent._create_client") as create:
        with TTSTencent("id", "key") as tts:
            with pytest.raises(TypeError, match="voice_type"):
                tts.text_to_voice("你好")
        create.return_value.call_json.assert_not_called()


@pytest.mark.parametrize(
    "options",
    [
        {"voice_type": True},
        {"voice_type": "1001"},
        {"voice_type": None},
        {"volume": -10.1},
        {"volume": 10.1},
        {"volume": True},
        {"speed": -2.01},
        {"speed": 6.01},
        {"speed": float("nan")},
        {"speed": float("inf")},
        {"primary_language": 3},
        {"sample_rate": 44100},
        {"codec": "aac"},
        {"enable_subtitle": 1},
        {"segment_rate": 3},
        {"emotion_category": "unknown"},
        {"emotion_intensity": 49},
        {"emotion_intensity": 201},
        {"emotion_intensity": 100.5},
        {"voice_type": 200000000},
        {"fast_voice_type": ""},
        {"codec": None},
    ],
)
def test_invalid_options_do_not_call_sdk(options: dict[str, Any]) -> None:
    with patch("jwf_common_python.tts.tencent.tencent._create_client") as create:
        with TTSTencent("id", "key") as tts:
            with pytest.raises(ValueError):
                tts.text_to_voice("你好", **{"voice_type": 1001, **options})
        create.return_value.call_json.assert_not_called()


def test_unknown_option_is_rejected() -> None:
    with pytest.raises(TypeError, match="speeed"):
        build_params("你好", 1001, None, {"speeed": 1})


@pytest.mark.parametrize(
    "options",
    [
        {"volume": -10, "speed": -2, "emotion_intensity": 50},
        {"volume": 10, "speed": 6, "emotion_intensity": 200},
        {"volume": 0, "speed": 0, "enable_subtitle": False, "segment_rate": 0},
    ],
)
def test_valid_boundaries_preserve_zero_and_false(options: dict[str, Any]) -> None:
    params = build_params("你好", 1001, "session", options)
    for name, value in options.items():
        assert params["".join(part.capitalize() for part in name.split("_"))] == value


@pytest.mark.parametrize(
    "kwargs",
    [
        {"secret_id": ""},
        {"secret_key": " "},
        {"secret_id": None},
        {"region": None},
        {"timeout": 0},
        {"timeout": -1},
        {"timeout": True},
        {"timeout": float("nan")},
        {"timeout": float("inf")},
        {"timeout": "5"},
    ],
)
def test_invalid_configuration_does_not_create_sdk(kwargs: dict[str, Any]) -> None:
    config = {"secret_id": "id", "secret_key": "key", **kwargs}
    with patch("jwf_common_python.tts.tencent.tencent._create_client") as create:
        with pytest.raises(ValueError):
            TTSTencent(**config)
        create.assert_not_called()


def test_legacy_sdk_without_persistent_session_can_close() -> None:
    sdk = Mock()
    sdk.request.conn = object()
    with patch("jwf_common_python.tts.tencent.tencent._create_client", return_value=sdk):
        with TTSTencent("id", "key"):
            pass
