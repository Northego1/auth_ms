from pathlib import Path
from typing import LiteralString, Self
from pydantic import BaseModel
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parents[1]


class DbSettings(BaseSettings):
    DB_NAME: str = 'auth'
    DB_HOST: str = 'localhost'
    DB_PORT: int = 5436
    DB_USER: str = 'postgres'
    DB_PASS: str = '0420'

    TEST_DB_NAME: str = 'test_auth'

    @property
    def postgres_dsn(self: Self) -> str:
        return (
            f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}'
            f'@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
        )


class RabbitMQSettings(BaseSettings):
    RMQ_HOST: str
    RMQ_PORT: int
    RMQ_USER: str
    RMQ_PASSWORD: str

    @property
    def rabbit_mq_dsn(self: Self) -> str:
        return f"amqp://{self.RMQ_USER}:{self.RMQ_PASSWORD}@{self.RMQ_HOST}/"


class AuthJwtSettings(BaseModel):
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
    jwt: AuthJwtSettings = AuthJwtSettings()
    db: DbSettings = DbSettings()


settings = Settings()