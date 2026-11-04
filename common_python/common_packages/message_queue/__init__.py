"""Kafka 和 RabbitMQ 消息队列；使用对应后端时才加载其可选依赖。"""

from .interface import MessageCallback, MessageQueue
from .kafka import KafkaQueue
from .rabbitmq import RabbitmqQueue

__all__ = ["MessageCallback", "MessageQueue", "KafkaQueue", "RabbitmqQueue"]
