"""消息队列的同步接口。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

MessageCallback = Callable[[bytes | None], None]


class MessageQueue(ABC):
    """消息以 bytes 传递（Kafka 删除标记为 None）。

    回调正常返回表示处理成功，抛出异常表示失败。
    消费采用至少一次处理语义，业务回调应能处理重复消息。
    实例不支持跨线程共享，使用 with 或 close() 释放连接。
    """

    def __init__(self) -> None:
        self._closed = False

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("消息队列已关闭")

    @staticmethod
    def _validate_item(item: bytes) -> None:
        if not isinstance(item, bytes):
            raise TypeError("item 必须为 bytes")

    @abstractmethod
    def enqueue(self, item: bytes) -> dict[str, Any] | None:
        """等待服务端确认发送；失败时抛出原始 SDK 异常。"""

    @abstractmethod
    def consumer(self, callback: MessageCallback) -> None:
        """阻塞消费；只在 callback 成功后确认消息，异常向调用方传播。"""

    @abstractmethod
    def close(self) -> None:
        """释放资源，可重复调用。"""

    def __enter__(self):
        self._ensure_open()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
