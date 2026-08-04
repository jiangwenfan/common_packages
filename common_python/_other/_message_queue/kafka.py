import logging


from common_packages._message_queue.interface import MessageQueue
from kafka import KafkaProducer
from kafka.errors import KafkaError


class KafkaQueue(MessageQueue):
    """kafka消息队列的实现封装"""

    # def __new__(cls):
    #     # 当使用kafka时,导入kafka库
    #     try:
    #         from kafka import KafkaProducer
    #         from kafka.errors import KafkaError
    #     except ImportError as exc:
    #         raise ImportError(
    #             "Couldn't import kafka. pip install --upgrade kafka-python"
    #         ) from exc
    #     else:
    #         cls.KafkaProducer = KafkaProducer
    #         cls.KafkaError = KafkaError

    #     return super().__new__()

    def __init__(self, **kwargs) -> None:
        # check bootstrap_servers and topic
        if not {"bootstrap_servers", "topic"}.issubset(kwargs.keys()):
            raise ValueError("bootstrap_servers and topic must be provided")

        # bootstrap_servers必须是list[str],example:  "localhost:9092"
        check_sub_element_result: bool = all(
            isinstance(element, str) for element in kwargs["bootstrap_servers"]
        )
        if not (
            isinstance(kwargs["bootstrap_servers"], list) and check_sub_element_result
        ):
            raise ValueError("bootstrap_servers must be list of str")

        # init kafka producer
        self.bootstrap_servers: list[str] = kwargs["bootstrap_servers"]
        self.topic: str = kwargs["topic"]
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers, retries=5
        )

    def enqueue(self, item: bytes, **kwargs) -> None:
        """
        key: bytes
            当需要保证消息顺序性时，传入相同的key，可以保证相同key的消息会被发送到同一个partition中
        """
        key = kwargs.get("key", None)
        if key:
            # produce keyed messages to enable hashed partitioning
            future = self.producer.send(self.topic, value=item, key=key)
        else:
            # produce asynchronously with callbacks
            future = self.producer.send(self.topic, value=item)

        # Block for 'synchronous' sends
        try:
            record_metadata = future.get(timeout=10)
        except KafkaError:
            # Decide what to do if produce request failed...
            logging.error(
                f"send message to kafka failed,\
                    {item.decode('utf-8')}, {KafkaError}"
            )
            assert True is False, "send message to kafka failed"
        else:
            response_result = {
                "topic": record_metadata.topic,
                "partition": record_metadata.partition,
                "offset": record_metadata.offset,
            }
            logging.info(f"send message to kafka success! {response_result=}")

    def message_callback(self, ch, method, properties, body: bytes) -> None:
        raise NotImplementedError

    def consumer(self) -> None:
        raise NotImplementedError
