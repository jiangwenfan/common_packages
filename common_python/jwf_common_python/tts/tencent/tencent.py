"""腾讯云基础语音合成 TextToVoice（Apifox 接口 524819309）。"""

from __future__ import annotations

from copy import deepcopy
from types import TracebackType
from typing import Any, Self, Unpack

from ._tencent_params import (
    TextToVoiceOptions,
    build_params,
    nonempty_string,
    positive_timeout,
)
from .tts import tts as voice_data

SDK_REQUIREMENT = "tencentcloud-sdk-python-common>=3.0.1042,<4"


def _create_client(secret_id: str, secret_key: str, region: str, timeout: float) -> Any:
    """按需加载公共 SDK，由 SDK 对最终请求体计算 TC3 签名。"""
    try:
        from tencentcloud.common.common_client import CommonClient
        from tencentcloud.common.credential import Credential
        from tencentcloud.common.profile.client_profile import ClientProfile
        from tencentcloud.common.profile.http_profile import HttpProfile
    except ImportError as exc:
        raise ImportError(
            f"请先安装腾讯云公共 SDK：pip install '{SDK_REQUIREMENT}'"
        ) from exc
    profile = ClientProfile()
    profile.httpProfile = HttpProfile(
        endpoint="tts.tencentcloudapi.com", reqTimeout=timeout
    )
    return CommonClient(
        "tts", "2019-08-23", Credential(secret_id, secret_key), region, profile
    )


def _response_body(response: Any) -> dict[str, Any]:
    """保留服务端字段；SDK 已负责检查 Response.Error。"""
    body = response.get("Response") if isinstance(response, dict) else None
    if not isinstance(body, dict) or not isinstance(body.get("Audio"), str):
        raise ValueError("腾讯语音合成响应缺少有效的 Audio")
    return body


class TTSTencent:
    """使用长期密钥合成短文本；不自动分段，不打印或保存音频。

    text_to_voice 返回完整 Response，音频由调用方按需解码。
    音色和语言支持范围、文本长度及 SSML 限制由腾讯云接口判定。
    """

    def __init__(
        self, secret_id: str, secret_key: str, *, region: str = "", timeout: float = 30
    ) -> None:
        nonempty_string("secret_id", secret_id)
        nonempty_string("secret_key", secret_key)
        if not isinstance(region, str):
            raise ValueError("region 必须为字符串，可留空")
        positive_timeout(timeout)
        self.client = _create_client(secret_id, secret_key, region, timeout)
        self._closed = False

    def text_to_voice(
        self,
        text: str,
        session_id: str | None = None,
        *,
        voice_type: int,
        **options: Unpack[TextToVoiceOptions],
    ) -> dict[str, Any]:
        """返回 Audio（Base64）、SessionId、Subtitles、RequestId 等原生字段。

        voice_type 必须显式指定；省略 session_id 时为每次请求生成 UUID。
        默认开启字幕、WAV 格式、正常语速和音量，可通过 options 覆盖。
        HTTP、网络及业务错误由 SDK 原样抛出，不将 HTTP 200 当成业务成功。
        """
        if self._closed:
            raise RuntimeError("腾讯语音合成客户端已关闭")
        params = build_params(text, voice_type, session_id, options)
        return _response_body(self.client.call_json("TextToVoice", params))

    @staticmethod
    def get_voices() -> list[dict[str, Any]]:
        """返回 tts.py 中的本地音色数据副本，无需密钥或网络请求。"""
        return deepcopy(voice_data)

    def close(self) -> None:
        """释放 SDK 的连接池；兼容无持久 Session 的旧版本 SDK。"""
        if not self._closed:
            try:
                session = getattr(self.client.request.conn, "_session", None)
                if session is not None:
                    session.close()
            finally:
                self._closed = True

    def __enter__(self) -> Self:
        if self._closed:
            raise RuntimeError("腾讯语音合成客户端已关闭")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()
