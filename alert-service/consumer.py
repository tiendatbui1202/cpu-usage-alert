import pika
import json
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from config import settings
from rabbit import get_channel
from seed import seed_thresholds

mongo = AsyncIOMotorClient(settings.MONGO_HOST, settings.MONGO_PORT,
                            username=settings.MONGO_USER, password=settings.MONGO_PASSWORD)
db = mongo[settings.MONGO_DB]

loop = asyncio.get_event_loop()


def serialize(doc: dict):
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            doc[k] = str(v)
    return doc


def get_level(value, t):
    if value >= t["critical"]:
        return "critical"
    if value >= t["warning"]:
        return "warning"
    return "normal"


async def process(data, ch):
    threshold = await db.thresholds.find_one(
        {"metric": data["metric"]}
    )

    if not threshold:
        return

    level = get_level(data["value"], threshold)
    if level == "normal" or level == "warning":
        return
    alert = {
        "device_id": data["device_id"],
        "metric": data["metric"],
        "value": data["value"],
        "level": level,
        "timestamp": data["timestamp"]
    }

    result = await db.alerts.insert_one(alert)
    alert["_id"] = result.inserted_id

    alert = serialize(alert)

    ch.basic_publish(
        exchange="alerts_exchange",
        routing_key="alert",
        body=json.dumps(alert).encode("utf-8"),
        properties=pika.BasicProperties(delivery_mode=2)
    )


def callback(ch, method, properties, body):
    data = json.loads(body)

    loop.run_until_complete(process(data, ch))

    ch.basic_ack(method.delivery_tag)


if __name__ == "__main__":
    loop.run_until_complete(seed_thresholds(db))
    channel = get_channel()
    channel.basic_consume(
        queue=settings.METRICS_QUEUE,
        on_message_callback=callback
    )
    print("Alert service waiting...")
    channel.start_consuming()
