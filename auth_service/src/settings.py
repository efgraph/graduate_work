import os
from datetime import timedelta

from pydantic import BaseSettings

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def build_dsn(
        protocol: str,
        user: str,
        password: str,
        host: str,
        port: int,
        path: str,
) -> str:
    return f'{protocol}://postgres:{password}@{host}:{port}/{path}'


class DatabaseSettings(BaseSettings):
    protocol: str = 'postgresql'
    user: str = os.environ['POSTGRES_USER']
    password: str = os.environ['POSTGRES_PASSWORD']
    host: str = os.environ['POSTGRES_HOST']
    port: int = os.environ['POSTGRES_PORT']
    name: str = os.environ['POSTGRES_DB']

    @property
    def dsn(self) -> str:
        return build_dsn(
            protocol=self.protocol,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            path=self.name,
        )


class RedisSettings(BaseSettings):
    host: str = os.environ['STORAGE_HOST']
    port: int = os.environ['STORAGE_PORT']


class JWTSettings(BaseSettings):
    access_token_expire_time: timedelta = timedelta(minutes=60)
    refresh_token_expire_time: timedelta = timedelta(days=7)
    token_location = ['headers', 'query_string']
    secret_key: str = os.environ['JWT_SECRET_KEY']


class WSGISettings(BaseSettings):
    host: str = 'localhost'
    port: int = 5000
    workers: int = 4


class GoogleAuthSettings(BaseSettings):
    name: str = 'google'
    server_metadata_url: str = 'https://accounts.google.com/.well-known/openid-configuration'
    client_id: str = os.environ['CLIENT_ID']
    client_secret: str = os.environ['CLIENT_SECRET']


class Settings(BaseSettings):
    db: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    jwt: JWTSettings = JWTSettings()
    wsgi: WSGISettings = WSGISettings()
    oauth = GoogleAuthSettings()


settings = Settings()
