import logging as log
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
    )

    name: str = Field(validation_alias="API_NAME")
    debug: bool = Field(validation_alias="API_DEBUG")
    version: str = Field(validation_alias="API_VERSION")

    host: str = Field(validation_alias="API_HOST", default="localhost")
    port: int = Field(validation_alias="API_PORT", default=8000)


@lru_cache()
def get_settings() -> Settings:
    return Settings()  # type: ignore