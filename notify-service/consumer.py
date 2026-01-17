import json
import requests
from config import settings
from rabbit import get_channel


def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": settings.CHAT_ID,
        "text": message
    })


def callback(ch, method, properties, body):
    alert = json.loads(body)

    message = (
        f"🚨 {alert['level'].upper()} ALERT\n"
        f"Device: {alert['device_id']}\n"
        f"Metric: {alert['metric']}\n"
        f"Value: {alert['value']}\n"
        f"Time: {alert['timestamp']}"
    )

    send_telegram(message)
    ch.basic_ack(method.delivery_tag)


if __name__ == "__main__":
    channel = get_channel()
    channel.basic_consume(
        queue=settings.ALERTS_QUEUE,
        on_message_callback=callback
    )
    print("Notify service waiting...")
    channel.start_consuming()
