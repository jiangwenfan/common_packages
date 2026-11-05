"""离线测试：使用真实 SDK 数据类型，模拟网络客户端。"""

import json
import subprocess
import sys
import unittest
from collections import namedtuple
from types import SimpleNamespace
from unittest.mock import Mock, call, patch

import kafka
import pika
from kafka.errors import KafkaTimeoutError
from kafka.structs import TopicPartition

from common_python.message_queue import KafkaQueue, RabbitmqQueue


class DependencyTests(unittest.TestCase):
    def test_package_import_does_not_require_either_sdk(self):
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import sys; sys.modules['kafka'] = None; sys.modules['pika'] = None; "
                    "from common_python.message_queue import KafkaQueue, RabbitmqQueue"
                ),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_missing_dependencies_give_install_instructions(self):
        with patch.dict(sys.modules, {"kafka": None, "pika": None}):
            with self.assertRaisesRegex(ImportError, "pip install kafka-python"):
                KafkaQueue(["localhost:9092"], "events")
            with self.assertRaisesRegex(ImportError, "pip install pika"):
                RabbitmqQueue("jobs", "localhost", username="user", password="secret")


class KafkaTests(unittest.TestCase):
    def setUp(self):
        producer_patch = patch.object(kafka, "KafkaProducer")
        consumer_patch = patch.object(kafka, "KafkaConsumer")
        self.producer_type = producer_patch.start()
        self.consumer_type = consumer_patch.start()
        self.addCleanup(producer_patch.stop)
        self.addCleanup(consumer_patch.stop)
        self.queue = KafkaQueue(["localhost:9092"], "events", group_id="workers")
        self.addCleanup(self.queue.close)

    def test_lazy_producer_and_binary_send_result(self):
        self.producer_type.assert_not_called()
        producer = self.producer_type.return_value
        producer.send.return_value.get.return_value = SimpleNamespace(
            topic="events", partition=1, offset=12
        )
        self.assertEqual(
            self.queue.enqueue(b"\xff", key=b""),
            {"topic": "events", "partition": 1, "offset": 12},
        )
        producer.send.assert_called_once_with("events", value=b"\xff", key=b"")
        producer.send.return_value.get.assert_called_once_with(timeout=10)
        config = self.producer_type.call_args.kwargs
        self.assertEqual(config["acks"], "all")
        self.assertEqual(config["max_in_flight_requests_per_connection"], 1)

    def test_send_failure_propagates_original_exception(self):
        error = KafkaTimeoutError("broker unavailable")
        self.producer_type.return_value.send.return_value.get.side_effect = error
        with self.assertRaises(KafkaTimeoutError) as caught:
            self.queue.enqueue(b"\xff")
        self.assertIs(caught.exception, error)

    def test_json_send_waits_for_confirmation_and_preserves_unicode(self):
        producer = self.producer_type.return_value
        producer.send.return_value.get.return_value = SimpleNamespace(
            topic="events", partition=0, offset=42
        )
        message = {"message": "你好", "nested": [True, None, 2]}
        result = self.queue.enqueue_json(message, key=b"user-1")
        payload = producer.send.call_args.kwargs["value"]
        self.assertEqual(json.loads(payload.decode("utf-8")), message)
        self.assertIn("你好".encode("utf-8"), payload)
        self.assertEqual(producer.send.call_args.kwargs["key"], b"user-1")
        producer.send.return_value.get.assert_called_once_with(timeout=10)
        self.assertEqual(result, {"topic": "events", "partition": 0, "offset": 42})
        producer.flush.assert_not_called()

    def test_json_serialization_errors_do_not_connect_to_kafka(self):
        for message in (
            {"invalid": object()},
            {"invalid": float("nan")},
            {"invalid": float("inf")},
        ):
            with self.subTest(message=message), self.assertRaises(
                (ValueError, TypeError)
            ):
                self.queue.enqueue_json(message)
        self.producer_type.assert_not_called()

    def test_json_send_prevents_double_serialization(self):
        queue = KafkaQueue(
            ["localhost:9092"],
            "events",
            producer_config={"value_serializer": lambda value: value},
        )
        self.addCleanup(queue.close)
        with self.assertRaisesRegex(ValueError, "value_serializer"):
            queue.enqueue_json({"message": "hello"})
        self.producer_type.assert_not_called()

    def test_json_send_propagates_delivery_failure(self):
        error = KafkaTimeoutError("broker unavailable")
        self.producer_type.return_value.send.return_value.get.side_effect = error
        with self.assertRaises(KafkaTimeoutError) as caught:
            self.queue.enqueue_json({"message": "hello"})
        self.assertIs(caught.exception, error)

    def test_consumption_commits_only_processed_partition(self):
        client = self.consumer_type.return_value
        messages = [
            SimpleNamespace(topic="events", partition=0, offset=4, value=b"one"),
            SimpleNamespace(topic="events", partition=1, offset=8, value=b"two"),
        ]
        client.__iter__.return_value = iter(messages)
        callback = Mock()
        self.queue.consumer(callback)

        callback.assert_has_calls([call(b"one"), call(b"two")])
        commits = client.commit.call_args_list
        self.assertEqual(len(commits), 2)
        self.assertEqual(
            set(commits[0].kwargs["offsets"]), {TopicPartition("events", 0)}
        )
        self.assertEqual(
            commits[0].kwargs["offsets"][TopicPartition("events", 0)].offset, 5
        )
        self.assertEqual(
            commits[1].kwargs["offsets"][TopicPartition("events", 1)].offset, 9
        )
        self.assertFalse(self.consumer_type.call_args.kwargs["enable_auto_commit"])
        client.close.assert_called_once_with(autocommit=False)
        self.producer_type.assert_not_called()

    def test_failed_callback_does_not_commit_prefetched_messages(self):
        client = self.consumer_type.return_value
        client.__iter__.return_value = iter(
            [
                SimpleNamespace(topic="events", partition=0, offset=0, value=b"one"),
                SimpleNamespace(topic="events", partition=0, offset=1, value=b"two"),
            ]
        )
        callback = Mock(side_effect=[None, ValueError("failed")])
        with self.assertRaisesRegex(ValueError, "failed"):
            self.queue.consumer(callback)
        client.commit.assert_called_once()
        committed = client.commit.call_args.kwargs["offsets"][
            TopicPartition("events", 0)
        ]
        self.assertEqual(committed.offset, 1)
        client.close.assert_called_once_with(autocommit=False)

    def test_supports_legacy_offset_metadata(self):
        self.queue._offset_metadata = namedtuple("OffsetAndMetadata", "offset metadata")
        client = self.consumer_type.return_value
        client.__iter__.return_value = iter(
            [SimpleNamespace(topic="events", partition=0, offset=0, value=b"one")]
        )
        self.queue.consumer(Mock())
        self.assertEqual(
            client.commit.call_args.kwargs["offsets"][
                TopicPartition("events", 0)
            ].offset,
            1,
        )

    def test_group_required_and_manual_commit_cannot_be_disabled(self):
        queue = KafkaQueue(["localhost:9092"], "events")
        with self.assertRaisesRegex(ValueError, "group_id"):
            queue.consumer(Mock())
        self.consumer_type.assert_not_called()
        with self.assertRaises(ValueError):
            KafkaQueue(
                ["localhost:9092"],
                "events",
                consumer_config={"enable_auto_commit": True},
            )

    def test_commit_failure_stops_consumption_and_releases_client(self):
        client = self.consumer_type.return_value
        client.__iter__.return_value = iter(
            [
                SimpleNamespace(topic="events", partition=0, offset=0, value=None),
                SimpleNamespace(topic="events", partition=0, offset=1, value=b"next"),
            ]
        )
        client.commit.side_effect = KafkaTimeoutError("commit failed")
        callback = Mock()
        with self.assertRaises(KafkaTimeoutError):
            self.queue.consumer(callback)
        callback.assert_called_once_with(None)
        client.close.assert_called_once_with(autocommit=False)

    def test_validation_context_manager_and_closed_state(self):
        for servers in ([], "localhost:9092", [None], [""]):
            with self.subTest(servers=servers), self.assertRaises(ValueError):
                KafkaQueue(servers, "events")
        with self.assertRaises(TypeError):
            self.queue.enqueue("text")
        with self.queue:
            producer = self.queue.producer
        self.queue.close()
        producer.close.assert_called_once_with(timeout=10)
        with self.assertRaises(RuntimeError):
            self.queue.enqueue(b"message")


class RabbitmqTests(unittest.TestCase):
    def setUp(self):
        connection_patch = patch.object(pika, "BlockingConnection")
        self.connection_type = connection_patch.start()
        self.addCleanup(connection_patch.stop)
        self.connection = self.connection_type.return_value
        self.connection.is_open = True
        self.channel = self.connection.channel.return_value

    def make_queue(self, **kwargs):
        queue = RabbitmqQueue(
            "jobs", "localhost", "5672", username="user", password="secret", **kwargs
        )
        self.addCleanup(queue.close)
        return queue

    def deliver(self, body):
        callback = self.channel.basic_consume.call_args.kwargs["on_message_callback"]
        callback(self.channel, SimpleNamespace(delivery_tag=7), None, body)

    def test_publish_is_persistent_confirmed_and_mandatory(self):
        queue = self.make_queue()
        self.channel.queue_declare.assert_called_once_with(queue="jobs", durable=True)
        self.channel.confirm_delivery.assert_called_once()
        self.assertEqual(self.connection_type.call_args.args[0].port, 5672)
        self.assertEqual(
            self.connection_type.call_args.args[0].blocked_connection_timeout, 30
        )
        queue.enqueue(b"\xff")
        kwargs = self.channel.basic_publish.call_args.kwargs
        self.assertEqual(kwargs["body"], b"\xff")
        self.assertEqual(kwargs["properties"].delivery_mode, 2)
        self.assertTrue(kwargs["mandatory"])

    def test_publish_failure_propagates(self):
        queue = self.make_queue()
        error = pika.exceptions.UnroutableError([])
        self.channel.basic_publish.side_effect = error
        with self.assertRaises(pika.exceptions.UnroutableError) as caught:
            queue.enqueue(b"message")
        self.assertIs(caught.exception, error)

    def test_ack_only_after_successful_callback(self):
        queue = self.make_queue()
        self.channel.start_consuming.side_effect = lambda: self.deliver(b"message")

        def callback(body):
            self.assertEqual(body, b"message")
            self.channel.basic_ack.assert_not_called()

        queue.consumer(callback)
        self.assertFalse(self.channel.basic_consume.call_args.kwargs["auto_ack"])
        self.channel.basic_qos.assert_called_once_with(prefetch_count=1)
        self.channel.basic_ack.assert_called_once_with(delivery_tag=7)
        self.channel.basic_nack.assert_not_called()
        self.connection.close.assert_called_once()

    def test_callback_failure_nacks_and_closes(self):
        for requeue in (True, False):
            with self.subTest(requeue=requeue):
                self.channel.reset_mock()
                self.connection.close.reset_mock()
                queue = self.make_queue(requeue_on_error=requeue)
                self.channel.start_consuming.side_effect = lambda: self.deliver(
                    b"message"
                )
                with self.assertRaisesRegex(ValueError, "failed"):
                    queue.consumer(Mock(side_effect=ValueError("failed")))
                self.channel.basic_ack.assert_not_called()
                self.channel.basic_nack.assert_called_once_with(
                    delivery_tag=7, requeue=requeue
                )
                self.connection.close.assert_called_once()

    def test_initialization_failure_releases_connection(self):
        self.channel.queue_declare.side_effect = RuntimeError("declare failed")
        with self.assertRaisesRegex(RuntimeError, "declare failed"):
            self.make_queue()
        self.connection.close.assert_called_once()

    def test_consumer_registration_failure_releases_connection(self):
        queue = self.make_queue()
        self.channel.basic_consume.side_effect = RuntimeError("registration failed")
        with self.assertRaisesRegex(RuntimeError, "registration failed"):
            queue.consumer(Mock())
        self.connection.close.assert_called_once()
        self.channel.start_consuming.assert_not_called()

    def test_non_durable_compatibility_and_idempotent_close(self):
        queue = self.make_queue(durable=False)
        queue.enqueue(b"message")
        self.assertEqual(
            self.channel.basic_publish.call_args.kwargs["properties"].delivery_mode, 1
        )
        with queue:
            pass
        queue.close()
        self.connection.close.assert_called_once()
        with self.assertRaises(RuntimeError):
            queue.enqueue(b"message")


if __name__ == "__main__":
    unittest.main()
