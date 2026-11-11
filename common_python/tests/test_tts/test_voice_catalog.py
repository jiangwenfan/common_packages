"""验证音色聚合结果、扩展字段及数据隔离；不访问外部服务。"""

from copy import deepcopy
from typing import Any
from unittest.mock import patch

import pytest

from jwf_common_python.tts import TTSTencent, TTSVoiceCatalog


COMMON_VOICE: dict[str, Any] = {
    "name": "智斌",
    "voice_id": 501000,
    "description": "磁性男声",
    "gender": "男",
    "supplier": "腾讯云",
    "category": "阅读",
}


def test_catalog_returns_local_tencent_voices_without_sdk() -> None:
    with patch("jwf_common_python.tts.tencent.tencent._create_client") as create:
        original = TTSTencent.get_voices()
        voices = TTSVoiceCatalog.get_voices()
        create.assert_not_called()
    assert len(voices) == len(original) == 5
    assert voices[0] == {
        **COMMON_VOICE,
        "other": {
            "languages": ["中文", "英文"],
            "sample_rates": [8000, 16000, 24000],
            "emotions": ["中性"],
            "enable_latex": False,
            "model": "大模型",
        },
    }
    for voice, source in zip(voices, original):
        assert set(voice) == {*COMMON_VOICE, "other"}
        assert {**{key: voice[key] for key in COMMON_VOICE}, **voice["other"]} == source


@pytest.mark.parametrize("extras", [{}, {"new_feature": ["value"], "enabled": False}])
def test_catalog_groups_arbitrary_extras_and_preserves_order(
    extras: dict[str, Any],
) -> None:
    sources = [dict(COMMON_VOICE, **extras), dict(COMMON_VOICE, voice_id="custom")]
    original = deepcopy(sources)
    with patch.object(TTSTencent, "get_voices", return_value=sources) as get_voices:
        voices = TTSVoiceCatalog.get_voices()
        get_voices.assert_called_once_with()
    assert voices == [
        {**COMMON_VOICE, "other": extras},
        {**COMMON_VOICE, "voice_id": "custom", "other": {}},
    ]
    assert sources == original


def test_catalog_returns_independent_nested_data() -> None:
    sources = [{**COMMON_VOICE, "languages": ["中文"], "metadata": {"tags": []}}]
    original = deepcopy(sources)
    with patch.object(TTSTencent, "get_voices", return_value=sources):
        voices = TTSVoiceCatalog.get_voices()
        voices[0]["name"] = "changed"
        voices[0]["other"]["languages"].append("英文")
        voices[0]["other"]["metadata"]["tags"].append("changed")
        voices.clear()
        assert TTSVoiceCatalog.get_voices() == [
            {**COMMON_VOICE, "other": {"languages": ["中文"], "metadata": {"tags": []}}}
        ]
    assert sources == original


def test_catalog_handles_empty_supplier_list() -> None:
    with patch.object(TTSTencent, "get_voices", return_value=[]):
        assert TTSVoiceCatalog.get_voices() == []
