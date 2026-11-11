"""从根目录 .env 读取 Azure Speech 配置，显式启用时真实合成。"""

from pathlib import Path

import pytest

from jwf_common_python.tts.azure import TTSMicrosoft

ROOT = Path(__file__).resolve().parents[2]


def read_config(env_path: Path) -> dict[str, str]:
    """读取本地配置并检查 Azure 必填项，不修改进程环境。"""
    from dotenv import dotenv_values

    if not env_path.is_file():
        raise ValueError("请复制 .env.example 为仓库根目录的 .env 并填写 Azure 配置")
    config = {key: value for key, value in dotenv_values(env_path).items() if value}
    for key in ("AZURE_SPEECH_KEY", "AZURE_SPEECH_REGION"):
        if not config.get(key, "").strip():
            raise ValueError(f"请在 .env 中填写 {key}")
    if config.get("AZURE_TTS_LANGUAGE", "zh") not in ("en", "zh"):
        raise ValueError("AZURE_TTS_LANGUAGE 仅支持 en 或 zh")
    return config


@pytest.mark.manual
def test_azure_tts_from_env() -> None:
    """获取令牌并真实合成一次，将 WAV 保存到忽略提交的测试目录。"""
    config = read_config(ROOT / ".env")
    tts = TTSMicrosoft(
        key=config["AZURE_SPEECH_KEY"],
        location_region=config["AZURE_SPEECH_REGION"],
        language=config.get("AZURE_TTS_LANGUAGE", "zh"),
    )
    audio = tts.convert_text_to_speech(
        config.get("AZURE_TTS_TEXT", "你好，这是 Azure 语音合成本地测试。")
    )
    assert audio[:4] == b"RIFF" and audio[8:12] == b"WAVE", "未返回有效 WAV 音频"
    audio_path = ROOT / "test_temp_data" / "azure_tts.wav"
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    audio_path.write_bytes(audio)
    print(f"\n音频：{audio_path}")
