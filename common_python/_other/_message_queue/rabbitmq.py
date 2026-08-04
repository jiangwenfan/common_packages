# import logging


from common_packages._message_queue.interface import MessageQueue


class RabbitmqQueue(MessageQueue):
    def __new__(cls):
        # 当使用rabbitmq时,导入pika库
        global BlockingChannel, Basic, BasicProperties
        try:
            import pika
            from pika.adapters.blocking_connection import BlockingChannel
            from pika.spec import Basic, BasicProperties
        except ImportError as exc:
            raise ImportError(
                "Couldn't import pika. pip install --upgrade pika"
            ) from exc
        else:
            cls.pika = pika
            # cls.BlockingChannel = BlockingChannel
            # cls.Basic = Basic
            # cls.BasicProperties = BasicProperties

        return super().__new__()

    def __init__(self, queue_name: str, host: str, port: str, **kwargs) -> None:
        if not {"username", "password"}.issubset(kwargs.keys()):
            raise ValueError("username and password must be provided")
        self.queue_name = queue_name
        credentials = self.pika.PlainCredentials(kwargs["username"], kwargs["password"])
        try:
            self.connect = self.pika.BlockingConnection(
                self.pika.ConnectionParameters(
                    host=host, port=port, credentials=credentials
                )
            )
        except Exception as e:
            raise ConnectionError(f"connect rabbitmq failed, {e}")
        try:
            self.channel = self.connect.channel()
        except Exception as e:
            raise ConnectionError(f"create channel failed, {e}")
        try:
            self.channel.queue_declare(queue=self.queue_name)
        except Exception as e:
            raise ConnectionError(f"create queue failed, {e}")

    def enqueue(self, item: bytes) -> None:
        self.channel.basic_publish(exchange="", routing_key=self.queue_name, body=item)

    # def message_callback(
    #     self,
    #     ch: BlockingChannel,  # type: ignore
    #     method: Basic.Deliver,  # type: ignore
    #     properties: BasicProperties,  # type: ignore
    #     body: bytes,
    # ) -> None:
    #     logging.info(f"consumer handle ok: {body.decode()}")

    # def consumer(self, welcome_message) -> None:  # type: ignore
    #     self.channel.basic_consume(
    #         queue=self.queue_name,
    #         auto_ack=True,
    #         on_message_callback=self.message_callback,
    #     )
    #     logging.info(f"consumer start success \n {welcome_message}")
    #     self.channel.start_consuming()
