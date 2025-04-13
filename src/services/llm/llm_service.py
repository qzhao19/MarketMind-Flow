from crewai import LLM
from typing import Optional
from pydantic import TypeAdapter
from functools import lru_cache

from .llm_config import LLMConfig

@lru_cache(maxsize=None)
def get_llm_config() -> LLMConfig:
    """Get singleton configuration instance with LRU caching"""
    return LLMConfig()


class LLMService:
    """LLM service encapsulation layer for unified management of LLM instance lifecycle
    """
    def __init__(self):
        self._adapter = TypeAdapter(LLMConfig)

    @lru_cache(maxsize=4)
    def get_client(self, config: Optional[dict] = None) -> LLM:
        """
        Get LLM Client (thread-safe)
        Args.
            config: optional configuration dictionary, takes precedence over environment variables
            
        Example.
            >>> # Default configuration
            >>> llm = LLMService().get_client()
            >>>
            >>> # Custom configuration
            >>> llm = LLMService().get_client({“model”: “llama3”})
        """
        final_config = self._resolve_config(config)
        return self._create_client(final_config)

    def _resolve_config(self, config: Optional[dict]) -> LLMConfig:
        if config:
            return self._adapter.validate_python(config)
        return get_llm_config()

    def _create_client(self, config: LLMConfig) -> LLM:
        return LLM(
            model=f"{config.provider}/{config.model}",
            base_url=config.base_url,
            api_key=config.api_key,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            timeout=config.timeout,
        )

