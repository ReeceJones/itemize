from pydantic_settings import BaseSettings


class Config(BaseSettings):
    DB_URI: str = 'sqlite+aiosqlite:///./db.sqlite3'
    ECHO_SQL: bool = True
    TABLE_CREATE_ON_STARTUP: bool = True
    TABLE_DROP_ON_STARTUP: bool = False
    JWT_SECRET: str = 'secret'
    JWT_ALGORITHM: str = 'HS256'
    JWT_EXPIRATION_MINUTES: int = 60 * 24 * 30
    PARSER_LOG_PAGEDATA: bool = True
    SERVER_URL: str = 'http://localhost:8000'


CONFIG = Config()

print(CONFIG)
