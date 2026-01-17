from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_USER: str
    MONGO_PASSWORD: str
    MONGO_DB: str

    RABBITMQ_HOST: str
    RABBITMQ_PORT: str
    RABBITMQ_USER: str
    RABBITMQ_PASS: str

    METRICS_EXCHANGE: str
    ALERTS_EXCHANGE: str

    METRICS_QUEUE: str
    ALERTS_QUEUE: str

    TELEGRAM_BOT_TOKEN: str
    CHAT_ID: str

    class Config:
        env_file = ".env"


settings = Settings()

