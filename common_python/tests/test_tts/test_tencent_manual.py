"""从根目录 .env 读取配置的真实语音合成测试，默认不运行。"""

import base64
import json
from pathlib import Path

import pytest

from jwf_common_python.tts.tencent import TTSTencent

ROOT = Path(__file__).resolve().parents[2]


def read_config(env_path: Path) -> dict[str, str]:
    """仅在手动测试时读取本地配置，不修改进程环境。"""
    from dotenv import dotenv_values

    if not env_path.is_file():
        raise ValueError("请复制 .env.example 为仓库根目录的 .env 并填写配置")
    config = {key: value for key, value in dotenv_values(env_path).items() if value}
    for key in (
        "TENCENTCLOUD_SECRET_ID", "TENCENTCLOUD_SECRET_KEY", "TENCENT_TTS_VOICE_TYPE",
    ):
        if not config.get(key, "").strip():
            raise ValueError(f"请在 .env 中填写 {key}")
    return config


@pytest.mark.manual
def test_tencent_tts_from_env() -> None:
    """真实调用一次，并保存音频和字幕响应供本地试听、检查。"""
    config = read_config(ROOT / ".env")
    voice_type = int(config["TENCENT_TTS_VOICE_TYPE"])
    with TTSTencent(
        secret_id=config["TENCENTCLOUD_SECRET_ID"],
        secret_key=config["TENCENTCLOUD_SECRET_KEY"],
    ) as tts:
        response = tts.text_to_voice(
            config.get("TENCENT_TTS_TEXT", "你好，这是腾讯云语音合成本地测试。"),
            voice_type=voice_type,
        )
    audio = base64.b64decode(response["Audio"], validate=True)
    assert audio[:4] == b"RIFF" and audio[8:12] == b"WAVE", "未返回有效 WAV 音频"
    output_dir = ROOT / "test_temp_data"
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_path = output_dir / "tencent_tts.wav"
    response_path = output_dir / "tencent_tts_response.json"
    audio_path.write_bytes(audio)
    response_path.write_text(
        json.dumps(response, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n音频：{audio_path}\n完整响应：{response_path}")
