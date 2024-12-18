from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path.cwd()/'.env', env_file_encoding='utf-8')
    
    db_user: str
    db_password: str
    db_name: str
    db_host: str
    db_port: int

settings = Settings()