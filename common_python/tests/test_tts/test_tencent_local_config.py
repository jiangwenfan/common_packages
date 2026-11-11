"""离线验证 .env 配置读取和手动测试的输出流程。"""

import base64
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from tests.test_tts import test_tencent_manual as manual

ENV = (
    'TENCENTCLOUD_SECRET_ID="test-id"\n'
    "TENCENTCLOUD_SECRET_KEY='test-key'\n"
    "TENCENT_TTS_VOICE_TYPE=1001\n"
)


def test_missing_env_file_has_setup_hint(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match=".env.example"):
        manual.read_config(tmp_path / ".env")


@pytest.mark.parametrize("key", [
    "TENCENTCLOUD_SECRET_ID", "TENCENTCLOUD_SECRET_KEY", "TENCENT_TTS_VOICE_TYPE",
])
def test_required_config_is_checked(tmp_path: Path, key: str) -> None:
    env_path = tmp_path / ".env"
    lines = [line for line in ENV.splitlines() if not line.startswith(f"{key}=")]
    env_path.write_text("\n".join(lines), encoding="utf-8")
    with pytest.raises(ValueError, match=key):
        manual.read_config(env_path)


def test_manual_flow_reads_env_and_saves_response(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text(ENV, encoding="utf-8")
    audio = b"RIFF\x00\x00\x00\x00WAVE"
    response = {
        "Audio": base64.b64encode(audio).decode(),
        "Subtitles": [], "RequestId": "offline-id",
    }
    with patch.object(manual, "ROOT", tmp_path), patch.object(manual, "TTSTencent") as tts:
        client = tts.return_value.__enter__.return_value
        client.text_to_voice.return_value = response
        manual.test_tencent_tts_from_env()
    tts.assert_called_once_with(secret_id="test-id", secret_key="test-key")
    client.text_to_voice.assert_called_once_with(
        "你好，这是腾讯云语音合成本地测试。", voice_type=1001
    )
    output_dir = tmp_path / "test_temp_data"
    assert (output_dir / "tencent_tts.wav").read_bytes() == audio
    assert json.loads((output_dir / "tencent_tts_response.json").read_text()) == response
