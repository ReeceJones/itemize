import logging

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    DB_URI: str = 'sqlite+aiosqlite:///./db.sqlite3'
    ECHO_SQL: bool = True
    TABLE_CREATE_ON_STARTUP: bool = True
    TABLE_DROP_ON_STARTUP: bool = False
    JWT_SECRET: str = 'secret'  # openssl rand -hex 32
    JWT_ALGORITHM: str = 'HS256'
    JWT_EXPIRATION_MINUTES: int = 60 * 24 * 30
    PARSER_LOG_PAGEDATA: bool = True
    SERVER_URL: str = 'http://localhost:8000'
    LOG_LEVEL: str = 'INFO'
    LOG_FORMAT: str = logging.BASIC_FORMAT


CONFIG = Config()
