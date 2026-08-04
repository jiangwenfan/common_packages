from abc import ABC, abstractmethod


class MessageQueue(ABC):
    @abstractmethod
    def __init__(self, queue_name: str, host: str, port: str, **kwargs) -> None:
        """检查配置，初始化连接对象"""
        ...

    @abstractmethod
    def enqueue(self, item: bytes) -> None:
        """实现消息入队方法"""
        ...

    @abstractmethod
    def message_callback(self, ch, method, properties, body: bytes) -> None:
        """实现消息回调方法，被消费者调用"""
        ...

    @abstractmethod
    def consumer(self) -> None:
        """消费者的阻塞方法"""
        ...
