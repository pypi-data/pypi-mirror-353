from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Config(BaseSettings):

    # Artifex settinfs
    API_KEY: Optional[str] = None
    DEFAULT_OUTPUT_PATH: str = f"{os.getcwd()}/artifex_output/"
    
    # Synthex settings
    DEFAULT_SYNTHEX_DATAPOINT_NUM: int = 10
    DEFAULT_SYNTHEX_DATASET_FORMAT: str = "csv"
    @property
    def DEFAULT_SYNTHEX_DATASET_NAME(self) -> str: 
        return f"train_data.{self.DEFAULT_SYNTHEX_DATASET_FORMAT}"
    
    # HuggingFace settings
    DEFAULT_HUGGINGFACE_BASE_MODEL: str = "bert-base-uncased"
    DEFAULT_HUGGINGFACE_LOGGING_LEVEL: str = "error"
    
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        extra="allow",
    )

    
config = Config()
