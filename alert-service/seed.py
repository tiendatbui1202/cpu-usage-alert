from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

DEFAULT_THRESHOLDS = [
    {
        "metric": "cpu_usage",
        "normal": 60,
        "warning": 70,
        "critical": 90
    },
    {
        "metric": "memory_usage",
        "normal": 65,
        "warning": 80,
        "critical": 95
    }
]


async def seed_thresholds(db):
    await db.thresholds.create_index(
        "metric",
        unique=True
    )

    for threshold in DEFAULT_THRESHOLDS:
        exists = await db.thresholds.find_one(
            {"metric": threshold["metric"]}
        )

        if not exists:
            await db.thresholds.insert_one(threshold)
            print(f"Seeded threshold: {threshold['metric']}")
        else:
            print(f"Threshold exists: {threshold['metric']}")
