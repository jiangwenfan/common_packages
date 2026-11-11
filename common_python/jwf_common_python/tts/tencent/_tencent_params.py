"""TextToVoice 参数类型及 Apifox 字段映射。"""

import math
from typing import Any, Literal, TypedDict
from uuid import uuid4


class TextToVoiceOptions(TypedDict, total=False):
    """可选业务参数；未提供时使用封装或服务端默认值。"""

    volume: float
    speed: float
    project_id: int
    model_type: int
    fast_voice_type: str
    primary_language: Literal[1, 2]
    sample_rate: Literal[8000, 16000, 24000]
    codec: Literal["wav", "mp3", "pcm"]
    enable_subtitle: bool
    segment_rate: Literal[0, 1, 2]
    emotion_category: str
    emotion_intensity: int


_CHOICES = {
    "primary_language": (1, 2),
    "sample_rate": (8000, 16000, 24000),
    "codec": ("wav", "mp3", "pcm"),
    "segment_rate": (0, 1, 2),
    "emotion_category": (
        "neutral", "sad", "happy", "angry", "fear", "news", "story", "radio",
        "poetry", "call", "sajiao", "disgusted", "amaze", "peaceful",
        "exciting", "aojiao", "jieshuo",
    ),
}
_RANGES = {"volume": (-10, 10), "speed": (-2, 6), "emotion_intensity": (50, 200)}
_INTEGERS = {
    "project_id", "model_type", "primary_language", "sample_rate",
    "segment_rate", "emotion_intensity",
}


def nonempty_string(name: str, value: object) -> None:
    """检查必填字符串，不修改文本或密钥。"""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} 必须为非空字符串")


def positive_timeout(timeout: float) -> None:
    """拒绝无效或无限的网络超时。"""
    if (
        isinstance(timeout, bool)
        or not isinstance(timeout, (int, float))
        or not math.isfinite(timeout)
        or timeout <= 0
    ):
        raise ValueError("timeout 必须为有限正数")


def _validate_option(name: str, value: Any) -> None:
    if name not in TextToVoiceOptions.__annotations__:
        raise TypeError(f"不支持的 TextToVoice 参数：{name}")
    if name in _INTEGERS:
        valid = isinstance(value, int) and not isinstance(value, bool)
    elif name in ("volume", "speed"):
        valid = (
            isinstance(value, (int, float))
            and not isinstance(value, bool) and math.isfinite(value)
        )
    elif name == "enable_subtitle":
        valid = isinstance(value, bool)
    else:
        valid = isinstance(value, str) and bool(value.strip())
    if not valid:
        raise ValueError(f"{name} 的参数类型或值无效")
    if name in _CHOICES and value not in _CHOICES[name]:
        raise ValueError(f"{name} 不在支持的范围内")
    if name in _RANGES and not _RANGES[name][0] <= value <= _RANGES[name][1]:
        raise ValueError(f"{name} 不在支持的范围内")


def build_params(
    text: str, voice_type: int, session_id: str | None, options: TextToVoiceOptions
) -> dict[str, Any]:
    """构建独立请求，避免跨调用共享参数或重复生成会话标识。"""
    nonempty_string("text", text)
    if isinstance(voice_type, bool) or not isinstance(voice_type, int):
        raise ValueError("voice_type 必须为整数")
    if session_id is None:
        session_id = str(uuid4())
    nonempty_string("session_id", session_id)
    params: dict[str, Any] = {
        "Text": text, "SessionId": session_id, "ModelType": 1,
        "VoiceType": voice_type, "PrimaryLanguage": 1, "SampleRate": 16000, "Codec": "wav",
        "EnableSubtitle": True, "Speed": 0, "Volume": 0,
    }
    for name, value in options.items():
        _validate_option(name, value)
        params["".join(part.capitalize() for part in name.split("_"))] = value
    if params["VoiceType"] == 200000000 and not params.get("FastVoiceType"):
        raise ValueError("一句话复刻音色必须提供 fast_voice_type")
    return params
