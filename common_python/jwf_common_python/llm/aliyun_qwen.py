"""阿里云通义千问翻译客户端，不依赖应用框架配置。"""

import logging
import threading
import time
from typing import Any

import requests

DASHSCOPE_CHAT_URL = (
    "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
)
DEFAULT_REQUEST_INTERVAL = 2.0
_MAX_RATE_LIMIT_RETRIES = 1
_request_lock = threading.Lock()
_last_request_started_at: float | None = None


def _wait_for_request_slot(interval: float) -> None:
    """所有客户端共享进程内请求间隔，包含重试请求。"""
    global _last_request_started_at
    with _request_lock:
        now = time.monotonic()
        if _last_request_started_at is not None:
            remaining = interval - (now - _last_request_started_at)
            if remaining > 0:
                time.sleep(remaining)
                now = time.monotonic()
        _last_request_started_at = now


class LLMAliyunQwen:
    """通过显式配置调用通义千问，默认相邻请求至少间隔两秒。"""

    def __init__(
        self, api_key: str, *, request_interval: float = DEFAULT_REQUEST_INTERVAL
    ):
        if not api_key:
            raise ValueError("请传入通义千问 api_key 参数")
        self.api_key = api_key
        self.request_interval = max(float(request_interval), 0.0)

    def translate_text(
        self,
        content: str,
        *,
        model: str = "qwen-mt-turbo",
        source_lang: str = "auto",
        target_lang: str = "Chinese",
        timeout: float = 60.0,
    ) -> dict[str, Any]:
        """调用翻译模型并返回完整 JSON；HTTP 和网络异常向调用方传递。"""
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": content}],
            "translation_options": {
                "source_lang": source_lang,
                "target_lang": target_lang,
            },
        }
        return self._post(payload, timeout)

    def _post(self, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
        """发送请求，遇到 429 时按相同间隔最多重试一次。"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        for attempt in range(_MAX_RATE_LIMIT_RETRIES + 1):
            _wait_for_request_slot(self.request_interval)
            response = requests.post(
                DASHSCOPE_CHAT_URL, headers=headers, json=payload, timeout=timeout
            )
            try:
                response.raise_for_status()
            except requests.HTTPError:
                if response.status_code != 429 or attempt >= _MAX_RATE_LIMIT_RETRIES:
                    raise
                logging.warning("通义千问翻译请求触发限流，将在请求间隔后重试 1 次")
                continue
            return response.json()
        raise RuntimeError("通义千问翻译请求未返回结果")

    @staticmethod
    def get_translated_text(result: dict[str, Any]) -> str:
        """从 completions 响应中取出翻译结果文本。"""
        return result["choices"][0]["message"]["content"]
