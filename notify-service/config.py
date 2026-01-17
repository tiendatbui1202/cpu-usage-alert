from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_USER: str
    MONGO_PASSWORD: str

    RABBITMQ_HOST: str
    RABBITMQ_PORT: str
    RABBITMQ_USER: str
    RABBITMQ_PASS: str

    METRICS_QUEUE: str
    ALERTS_QUEUE: str

    METRICS_EXCHANGE: str
    ALERTS_EXCHANGE: str

    TELEGRAM_BOT_TOKEN: str
    CHAT_ID: str

    class Config:
        env_file = ".env"


settings = Settings()

