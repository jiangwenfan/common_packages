from kafka import KafkaProducer
import json


def create_producer(bootstrap_servers):
    """创建一个Kafka生产者"""
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        # 序列化器，这里使用JSON序列化
        value_serializer=lambda x: json.dumps(x).encode("utf-8"),
    )
    return producer


def send_message(producer, topic, message):
    """发送消息到Kafka"""
    # 发送消息，这里消息体是一个字典
    producer.send(topic, value=message)
    producer.flush()  # 确保所有消息都被发送出去


# 主函数，配置服务器地址和消息内容
if __name__ == "__main__":
    servers = "127.0.0.1:9092"  # Kafka服务器地址，根据实际情况修改
    topic_name = "test_kafka_topic"  # Kafka主题名称，确保这个主题已经存在
    message = {"message": "Hello"}  # 要发送的消息内容

    # 创建生产者
    kafka_producer = create_producer(servers)
    # 发送消息
    send_message(kafka_producer, topic_name, message)
    print("Message sent to Kafka!")
