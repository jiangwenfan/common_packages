"""基于 kafka-python 的同步生产和消费。"""

from __future__ import annotations

import json
from typing import Any

from .interface import MessageCallback, MessageQueue


class KafkaQueue(MessageQueue):
    def __init__(
        self,
        bootstrap_servers: list[str],
        topic: str,
        *,
        group_id: str | None = None,
        timeout: float = 10,
        producer_config: dict[str, Any] | None = None,
        consumer_config: dict[str, Any] | None = None,
    ) -> None:
        """连接按需创建，消费时必须提供 group_id。

        config 参数透传 SDK 配置，例如 SSL/SASL；连接地址、消费组和
        手动确认配置由本类管理，不能通过 config 覆盖。
        """
        super().__init__()
        if not isinstance(bootstrap_servers, list) or not bootstrap_servers:
            raise ValueError("bootstrap_servers 必须为非空 list[str]")
        if not all(
            isinstance(server, str) and server.strip() for server in bootstrap_servers
        ):
            raise ValueError("bootstrap_servers 必须为非空 list[str]")
        if not isinstance(topic, str) or not topic.strip():
            raise ValueError("topic 不能为空")
        if group_id is not None and (
            not isinstance(group_id, str) or not group_id.strip()
        ):
            raise ValueError("group_id 不能为空")
        if timeout <= 0:
            raise ValueError("timeout 必须大于 0")
        self._producer_config = dict(producer_config or {})
        self._consumer_config = dict(consumer_config or {})
        if "bootstrap_servers" in self._producer_config:
            raise ValueError("请通过 bootstrap_servers 参数设置连接地址")
        if {
            "bootstrap_servers",
            "group_id",
            "enable_auto_commit",
        } & self._consumer_config.keys():
            raise ValueError("consumer_config 不能覆盖连接地址、消费组或手动确认配置")

        try:
            import kafka
            from kafka.structs import OffsetAndMetadata, TopicPartition
        except ImportError as exc:
            raise ImportError("请先安装 Kafka 依赖：pip install kafka-python") from exc

        self._kafka = kafka
        self._offset_metadata = OffsetAndMetadata
        self._topic_partition = TopicPartition
        self.bootstrap_servers = list(bootstrap_servers)
        self.topic = topic
        self.group_id = group_id
        self.timeout = timeout
        self._producer = None

    @property
    def producer(self):
        """首次发送或访问此属性时创建生产者。"""
        self._ensure_open()
        if self._producer is None:
            config = {
                "acks": "all",
                "retries": 5,
                "max_in_flight_requests_per_connection": 1,
                **self._producer_config,
            }
            self._producer = self._kafka.KafkaProducer(
                bootstrap_servers=self.bootstrap_servers, **config
            )
        return self._producer

    def enqueue(self, item: bytes, *, key: bytes | None = None) -> dict[str, Any]:
        """同步发送并返回 topic、partition、offset；支持二进制内容和空 key。"""
        self._ensure_open()
        self._validate_item(item)
        if key is not None and not isinstance(key, bytes):
            raise TypeError("key 必须为 bytes 或 None")
        metadata = self.producer.send(self.topic, value=item, key=key).get(
            timeout=self.timeout
        )
        return {
            "topic": metadata.topic,
            "partition": metadata.partition,
            "offset": metadata.offset,
        }

    def enqueue_json(self, message: Any, *, key: bytes | None = None) -> dict[str, Any]:
        """发送 UTF-8 JSON，等待确认并返回 topic、partition、offset。

        不可序列化的内容或 NaN/Infinity 在连接前报错；不能同时配置
        value_serializer，避免对已编码 JSON 二次序列化。None 发送为 JSON null。
        """
        self._ensure_open()
        if self._producer_config.get("value_serializer") is not None:
            raise ValueError("enqueue_json 负责序列化，不能再配置 value_serializer")
        payload = json.dumps(
            message, ensure_ascii=False, allow_nan=False, separators=(",", ":")
        ).encode("utf-8")
        return self.enqueue(payload, key=key)

    def consumer(self, callback: MessageCallback) -> None:
        self._ensure_open()
        if not callable(callback):
            raise TypeError("callback 必须可调用")
        if self.group_id is None:
            raise ValueError("消费时必须提供 group_id，用于提交消费进度")
        client = self._kafka.KafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            enable_auto_commit=False,
            **self._consumer_config,
        )
        try:
            for message in client:
                callback(message.value)
                # 只提交已处理消息所在分区的下一条 offset，避免确认预取的其他消息。
                partition = self._topic_partition(message.topic, message.partition)
                offset = {"offset": message.offset + 1, "metadata": ""}
                # kafka-python 2.1+ 的 OffsetAndMetadata 新增了必填 leader_epoch。
                if "leader_epoch" in self._offset_metadata._fields:
                    offset["leader_epoch"] = getattr(message, "leader_epoch", -1)
                client.commit(offsets={partition: self._offset_metadata(**offset)})
        finally:
            client.close(autocommit=False)

    def close(self) -> None:
        if not self._closed:
            try:
                if self._producer is not None:
                    self._producer.close(timeout=self.timeout)
            finally:
                self._closed = True
