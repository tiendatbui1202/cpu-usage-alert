import pika
import json
from datetime import datetime
from config import settings
import time

_connection = None
_channel = None


def get_channel():
    global _connection, _channel

    if _channel:
        return _channel
    credentials = pika.PlainCredentials(
        settings.RABBITMQ_USER,
        settings.RABBITMQ_PASS
    )

    for i in range(10):
        try:
            _connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=settings.RABBITMQ_HOST,
                    port=settings.RABBITMQ_PORT,
                    credentials=credentials,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
            )
            _channel = _connection.channel()

            _channel.exchange_declare(
                exchange=settings.METRICS_EXCHANGE,
                exchange_type="direct",
                durable=True
            )

            return _channel

        except pika.exceptions.AMQPConnectionError:
            print(f"RabbitMQ not ready, retry {i+1}/10")
            time.sleep(3)

    raise RuntimeError("Cannot connect to RabbitMQ")

#
# credentials = pika.PlainCredentials(
#     settings.RABBITMQ_USER,
#     settings.RABBITMQ_PASS
# )


# connection = pika.BlockingConnection(
#     pika.ConnectionParameters(
#         host=settings.RABBITMQ_HOST,
#         port=settings.RABBITMQ_PORT,
#         credentials=credentials
#     )
# )
# channel = connection.channel()
#
# channel.exchange_declare(
#     exchange=settings.METRICS_EXCHANGE,
#     exchange_type="direct",
#     durable=True
# )


def publish_metric(data: dict):
    def default(o):
        if isinstance(o, datetime):
            return o.isoformat()
        raise TypeError

    channel = get_channel()

    channel.basic_publish(
        exchange=settings.METRICS_EXCHANGE,
        routing_key="metric",
        body=json.dumps(data, default=default).encode('utf-8'),
        properties=pika.BasicProperties(
            delivery_mode=2  # persistent
        )
    )

