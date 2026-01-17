import pika
import time
from config import settings

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
                    credentials=credentials
                )
            )

            _channel = _connection.channel()

            _channel.exchange_declare(
                exchange=settings.ALERTS_EXCHANGE,
                exchange_type="direct",
                durable=True
            )

            _channel.queue_declare(
                queue=settings.ALERTS_QUEUE,
                durable=True
            )

            _channel.queue_bind(
                exchange=settings.ALERTS_EXCHANGE,
                queue=settings.ALERTS_QUEUE,
                routing_key="alert"
            )

            print("Notify-service connected to RabbitMQ")
            return _channel

        except pika.exceptions.AMQPConnectionError:
            print(f"RabbitMQ not ready (notify), retry {i+1}/10")
            time.sleep(3)

    raise RuntimeError("Notify-service cannot connect to RabbitMQ")
