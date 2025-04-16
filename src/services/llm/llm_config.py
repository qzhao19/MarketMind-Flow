from crewai import LLM
from typing import Optional, Type
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from functools import lru_cache
from src.config.settings import LLM_BASE_URL, LLM_API_KEY, LLM_MODEL, LLM_PROVIDER

# Configuration class for LLM
class LLMConfig(BaseSettings):
    """
    Enhanced configuration class for LLM with environment variables support
    and runtime validation.
    
    Features:
    - Auto-loading from .env/environment variables
    - Field value validation
    - Cached configuration instances
    """
    base_url: str = Field(
        default=LLM_BASE_URL,
        description="Base API endpoint URL",
        env="LLM_BASE_URL"
    )
    api_key: str = Field(
        default=LLM_API_KEY, 
        description="API key for authentication",
        env="LLM_API_KEY"
    )
    model: str = Field(
        default=LLM_MODEL,
        description="Model name and version",
        env="LLM_MODEL"
    )
    provider: str = Field(
        default=LLM_PROVIDER,
        description="LLM provider name",
        env="LLM_PROVIDER"
    )
    temperature: float = Field(
        default=0.5,
        ge=0,
        le=1,
        description="Control randomness (0=deterministic, 1=creative)"
    )
    max_tokens: int = Field(
        default=2048,
        gt=0,
        description="Maximum length of generated response"
    )
    timeout: int = Field(
        default=600,
        gt=0,
        description="Request timeout in seconds"
    )

    @field_validator('base_url')
    def validate_base_url(cls, v: str) -> str:
        """Ensure API base URL follows expected format"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("Invalid protocol, must start with http:// or https://")
        if v.endswith('/'):
            raise ValueError("Base URL should not end with a slash")
        return v.rstrip('/')  # Normalize URL
    
    @field_validator('model')
    def validate_model(cls, v: str) -> str:
        """make sure the model not contain prefix 'provider'"""
        if '/' in v:
            raise ValueError("Model name should not include provider prefix")
        return v

