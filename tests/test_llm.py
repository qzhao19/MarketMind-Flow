import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

sys.path.append(str(Path(__file__).parent.parent))
from src.core.llm.models import LLMConfig, create_llm_client

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

LLM_CLASS_PATH = "src.core.llm.models.LLM"  # Update this to actual import path

class TestCreateLLMClient:
    """Test cases for create_llm_client function"""

    @patch(LLM_CLASS_PATH)  # Patch the original LLM class import
    def test_init_with_default_config(self, mock_llm_class):
        """Verify initialization with default configuration"""
        # Setup mock
        mock_instance = MagicMock()
        mock_llm_class.return_value = mock_instance

        # Execute
        result = create_llm_client()

        # Verify
        mock_llm_class.assert_called_once_with(
            model="qwen2.5:0.5b",
            base_url="http://localhost:11434/v1",
            api_key="ollama",
            temperature=0.5,
            max_tokens=2048,
            timeout=600
        )
        assert result is mock_instance

    @patch(LLM_CLASS_PATH)
    def test_init_with_custom_config(self, mock_llm_class):
        """Verify initialization with custom configuration"""
        # Setup
        custom_config = LLMConfig(
            model="custom_model",
            temperature=0.8,
            max_tokens=1024
        )
        mock_instance = MagicMock()
        mock_llm_class.return_value = mock_instance

        # Execute
        result = create_llm_client(config=custom_config)

        # Verify
        mock_llm_class.assert_called_once_with(
            model="custom_model",
            base_url="http://localhost:11434/v1",
            api_key="ollama",
            temperature=0.8,
            max_tokens=1024,
            timeout=600
        )
        assert result is mock_instance

    @patch(LLM_CLASS_PATH)
    def test_return_type(self, mock_llm_class):
        """Ensure function returns correct instance type"""
        mock_instance = MagicMock()
        mock_llm_class.return_value = mock_instance
        assert isinstance(create_llm_client(), MagicMock)
