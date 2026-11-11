"""离线验证 Azure 本地配置、手动调用和音频保存。"""

from pathlib import Path
from unittest.mock import patch

import pytest

from tests.test_tts import test_azure_manual as manual

ENV = 'AZURE_SPEECH_KEY="test-key"\nAZURE_SPEECH_REGION=eastasia\n'


def test_missing_env_file_has_setup_hint(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match=".env.example"):
        manual.read_config(tmp_path / ".env")


@pytest.mark.parametrize("key", ["AZURE_SPEECH_KEY", "AZURE_SPEECH_REGION"])
def test_required_config_is_checked(tmp_path: Path, key: str) -> None:
    env_path = tmp_path / ".env"
    lines = [line for line in ENV.splitlines() if not line.startswith(f"{key}=")]
    env_path.write_text("\n".join(lines), encoding="utf-8")
    with pytest.raises(ValueError, match=key):
        manual.read_config(env_path)


def test_invalid_language_is_rejected(tmp_path: Path) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text(ENV + "AZURE_TTS_LANGUAGE=invalid\n", encoding="utf-8")
    with pytest.raises(ValueError, match="AZURE_TTS_LANGUAGE"):
        manual.read_config(env_path)


@pytest.mark.parametrize("language", [None, "en"])
def test_manual_flow_reads_env_and_saves_audio(
    tmp_path: Path, language: str | None,
) -> None:
    config = ENV if language is None else ENV + f"AZURE_TTS_LANGUAGE={language}\n"
    config += 'AZURE_TTS_TEXT="Hello & 你好"\n'
    (tmp_path / ".env").write_text(config, encoding="utf-8")
    audio = b"RIFF\x00\x00\x00\x00WAVE"
    with (
        patch.object(manual, "ROOT", tmp_path),
        patch.object(manual, "TTSMicrosoft") as tts,
    ):
        tts.return_value.convert_text_to_speech.return_value = audio
        manual.test_azure_tts_from_env()
    tts.assert_called_once_with(
        key="test-key", location_region="eastasia", language=language or "zh",
    )
    tts.return_value.convert_text_to_speech.assert_called_once_with("Hello & 你好")
    assert (tmp_path / "test_temp_data" / "azure_tts.wav").read_bytes() == audio
