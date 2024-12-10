
from pathlib import Path
from typing import LiteralString, Self
from pydantic import BaseModel

# connection_params = pika.ConnectionParameters(
#     host=RMQ_HOST,
#     port=RMQ_PORT,
#     credentials=pika.PlainCredentials(RMQ_USER, RMQ_PASSWORD),
# )


# def get_connection() -> pika.BlockingConnection:
#     return pika.BlockingConnection(
#         parameters=connection_params,
#     )
BASE_DIR = Path(__file__).resolve().parents[1]


class DB:
    DB_NAME: str = 'auth'
    DB_HOST: str = 'localhost'
    DB_PORT: int = 5432
    DB_USER: str = 'postgres'
    DB_PASS: str = '0420'


    @property
    def postgres_dsn(self: Self) -> str:
        return (
            f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}'
            f'@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
        )


class RabbitMQSettings:
    RMQ_HOST: str= "0.0.0.0"
    RMQ_PORT: int = 5672
    RMQ_USER: str = "guest"
    RMQ_PASSWORD: str = "guest"


    @property
    def rabbit_mq_dsn(self: Self) -> str:
        return f"amqp://{self.RMQ_USER}:{self.RMQ_PASSWORD}@{self.RMQ_HOST}/"


class AuthJwt(BaseModel):
    private_key: str = (
        BASE_DIR / "consumer" / "jwt_certs" / "jwt-private.pem"
    ).read_text()
    public_key: str = (
        BASE_DIR / "consumer" / "jwt_certs" / "jwt-public.pem"
    ).read_text()

    algorithm: str = "RS256"
    type_field: str = "type"
    access_type: str = "access"
    refresh_type: str = "refresh"

    refresh_expire: int = 43200 # minutes (30 days)
    access_expire: int = 10 # minutes

    max_user_sessions: int = 5


class Settings:
    rabbit: RabbitMQSettings = RabbitMQSettings()
    jwt: AuthJwt = AuthJwt()
    db: DB = DB()


settings = Settings()