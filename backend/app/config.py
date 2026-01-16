from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    test_database_url: str = "sqlite:///./test.db"

    model_config = ConfigDict(env_file="../.env")

settings = Settings()