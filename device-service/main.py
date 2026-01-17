from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from datetime import datetime
from rabbit import publish_metric
from config import settings
app = FastAPI()
mongo = AsyncIOMotorClient(settings.MONGO_HOST, settings.MONGO_PORT,
                            username=settings.MONGO_USER, password=settings.MONGO_PASSWORD)
db = mongo[settings.MONGO_DB]


class MetricIn(BaseModel):
    device_id: str
    metric: str
    value: float
    timestamp: datetime


@app.post("/metrics")
async def ingest_metric(data: MetricIn):
    await db.metrics.insert_one(data.dict())
    publish_metric(data.dict())
    return {"status": "accepted"}
