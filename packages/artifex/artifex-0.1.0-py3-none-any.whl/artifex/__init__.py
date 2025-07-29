from synthex import Synthex
from typing import Optional
from transformers import logging as hf_logging

from .decorators import auto_validate_methods
from .guardrail import Guardrail
from .config import config
from .exceptions import ConfigurationError


if config.DEFAULT_HUGGINGFACE_LOGGING_LEVEL.lower() == "error":
    hf_logging.set_verbosity_error()


@auto_validate_methods
class Artifex:
    """
    Artifex is a library for easily training small AI models without data.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initializes Artifex with an API key for authentication.
        Args:
            api_key (Optional[str]): The API key to use for authentication. If not provided, attempts to load it from the .env file.
        """
        
        if not api_key:
            api_key=config.API_KEY
        if not api_key:
            raise ConfigurationError(
                "An API key is required. Please provide it as an argument, or create a .env file with a API_KEY entry in the project's root."
            )
        _synthex_client = Synthex(api_key=api_key)
        self.guardrail = Guardrail(synthex=_synthex_client)