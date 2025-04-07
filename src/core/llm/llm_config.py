from crewai import LLM
from typing import Optional, Type
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from functools import lru_cache
from src.config.settings import BASE_URL, API_KEY, MODEL 

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
        default=BASE_URL,
        description="Base API endpoint URL",
        env="LLM_BASE_URL"
    )
    api_key: str = Field(
        default=API_KEY, 
        description="API key for authentication",
        env="LLM_API_KEY"
    )
    model: str = Field(
        default=MODEL,
        description="Model name and version",
        env="LLM_MODEL"
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
        if not v.endswith('/v1'):
            raise ValueError("API path must end with /v1")
        return v.rstrip('/')  # Normalize URL

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "forbid"  # Disallow undefined fields

@lru_cache(maxsize=None)
def get_llm_config() -> LLMConfig:
    """Get singleton configuration instance with LRU caching"""
    return LLMConfig()

def create_llm_client(config: Optional[LLMConfig] = None) -> LLM:
    """
    Factory function for creating LLM client instances.
    
    Args:
        config: Custom configuration (uses cached default if None)
    
    Returns:
        Fully configured LLM client instance
    
    Example:
        >>> # Basic usage
        >>> llm = create_llm_client()
        >>>
        >>> # Custom configuration
        >>> custom_config = LLMConfig(model="qwen2.5:1b")
        >>> llm = create_llm_client(config=custom_config)
    """
    final_config = config or get_llm_config()
    return LLM(
        model=final_config.model,
        base_url=final_config.base_url,
        api_key=final_config.api_key,
        temperature=final_config.temperature,
        max_tokens=final_config.max_tokens,
        timeout=final_config.timeout,
    )