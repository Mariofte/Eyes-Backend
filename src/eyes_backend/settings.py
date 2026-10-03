from functools import lru_cache # cache para una sola instancia de configuración
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Configuración de la api
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
    
    # api settings
    name : str = Field(alias="API_NAME")
    debug : bool = Field(alias="API_DEBUG")
    version : str = Field(alias="API_VERSION")
    
    # uuvicorn settings
    host : str = Field(alias="API_HOST", default="localhost")
    port : int = Field(alias="API_PORT", default=8000)

@lru_cache() 
def get_settings() -> Settings:
    return Settings() # type: ignore