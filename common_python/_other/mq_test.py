import sys

sys.path.append("..")
from common_packages._message_queue import KafkaQueue
from common_packages._message_queue.rabbitmq import RabbitmqQueue

from ..tests import get_config


class TestRabbitmqQueue:
    def test_enqueue(self):
        config: dict = get_config()
        rabbitmq = RabbitmqQueue(**config["message_queue"]["rabbitmq"])
        rabbitmq.enqueue(b"hello world")

    def test_consumer(self):
        config: dict = get_config()
        rabbitmq = RabbitmqQueue(**config["message_queue"]["rabbitmq"])
        rabbitmq.consumer()


class TestKafkaQueue:
    def test_enqueue(self):
        config: dict = get_config()
        print(config["message_queue"]["kafka"])
        kafka = KafkaQueue(**config["message_queue"]["kafka"])
        kafka.enqueue(b"hello world")

    # def test_consumer(self):
    #     config: dict = get_config()
    #     kafka = KafkaQueue(
    #         **config["message_queue"]["kafka"]
    #     )
    #     kafka.consumer()
