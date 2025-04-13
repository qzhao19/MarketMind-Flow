import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# sys.path.append(str(Path(__file__).parent.parent))
from src.services.llm.llm_config import LLMConfig

class TestLLMConfig:
    """Test cases for LLMConfig class"""
    def test_default_values(self):
        """Test that default values are correctly set"""
        config = LLMConfig()
        assert config.base_url == "http://localhost:11434/v1"
        assert config.api_key == "ollama"
        assert config.model == "qwen2.5:0.5b"
        assert config.temperature == 0.5
        assert config.max_tokens == 2048
        assert config.timeout == 600
    
    @patch.dict(os.environ, {
        "LLM_BASE_URL": "http://test:8000",
        "LLM_API_KEY": "test_key",
        "LLM_MODEL": "test_model"
    })

    @pytest.mark.parametrize("temperature", [-0.1, 1.1])
    def test_temperature_validation(self, temperature):
        """Test temperature range validation (0-1)"""
        with pytest.raises(ValueError):
            LLMConfig(temperature=temperature)

