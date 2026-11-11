"""基于 pika BlockingConnection 的同步生产和消费。"""

from __future__ import annotations

from typing import Any

from .interface import MessageCallback, MessageQueue


class RabbitmqQueue(MessageQueue):
    def __init__(
        self,
        queue_name: str,
        host: str,
        port: int | str = 5672,
        *,
        username: str,
        password: str,
        durable: bool = True,
        prefetch_count: int = 1,
        requeue_on_error: bool = True,
        connection_config: dict[str, Any] | None = None,
    ) -> None:
        """默认持久化队列和消息，并启用发布确认。

        若已有同名非持久化队列，应传 durable=False，与服务端保持一致。
        connection_config 可传 virtual_host、SSL 等 pika 连接配置。
        """
        super().__init__()
        if not isinstance(queue_name, str) or not queue_name.strip():
            raise ValueError("queue_name 不能为空")
        if not isinstance(host, str) or not host.strip():
            raise ValueError("host 不能为空")
        port = int(port)
        if not 1 <= port <= 65535:
            raise ValueError("port 必须在 1 到 65535 之间")
        if not isinstance(prefetch_count, int) or prefetch_count <= 0:
            raise ValueError("prefetch_count 必须为正整数")
        config = dict(connection_config or {})
        if {"host", "port", "credentials"} & config.keys():
            raise ValueError("请通过独立参数设置 host、port、username 和 password")
        try:
            import pika
        except ImportError as exc:
            raise ImportError("请先安装 RabbitMQ 依赖：pip install pika") from exc

        self.pika = pika
        self.queue_name = queue_name
        self.durable = durable
        self.prefetch_count = prefetch_count
        self.requeue_on_error = requeue_on_error
        self.connect = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=host,
                port=port,
                credentials=pika.PlainCredentials(username, password),
                **{"blocked_connection_timeout": 30, **config},
            )
        )
        try:
            self.channel = self.connect.channel()
            self.channel.queue_declare(queue=queue_name, durable=durable)
            self.channel.confirm_delivery()
        except BaseException:
            self.close()
            raise

    def enqueue(self, item: bytes) -> None:
        self._ensure_open()
        self._validate_item(item)
        self.channel.basic_publish(
            exchange="",
            routing_key=self.queue_name,
            body=item,
            properties=self.pika.BasicProperties(
                delivery_mode=2 if self.durable else 1
            ),
            mandatory=True,
        )

    def consumer(self, callback: MessageCallback) -> None:
        self._ensure_open()
        if not callable(callback):
            raise TypeError("callback 必须可调用")

        def on_message(channel, method, properties, body):
            try:
                callback(body)
            except Exception:
                channel.basic_nack(
                    delivery_tag=method.delivery_tag, requeue=self.requeue_on_error
                )
                raise
            else:
                channel.basic_ack(delivery_tag=method.delivery_tag)

        try:
            self.channel.basic_qos(prefetch_count=self.prefetch_count)
            self.channel.basic_consume(
                queue=self.queue_name, on_message_callback=on_message, auto_ack=False
            )
            self.channel.start_consuming()
        finally:
            # 关闭连接也会使尚未确认的消息重新可消费，避免遗留活动消费者。
            self.close()

    def close(self) -> None:
        if not self._closed:
            try:
                if self.connect.is_open:
                    self.connect.close()
            finally:
                self._closed = True
