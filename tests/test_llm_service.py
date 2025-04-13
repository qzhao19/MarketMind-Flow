import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# sys.path.append(str(Path(__file__).parent.parent))
from src.services.llm.llm_config import LLMConfig
from src.services.llm.llm_service import LLMService


LLM_CLASS_PATH = "src.core.llm.llm_config.LLM"  # Update this to actual import path

class TestCreateLLMClient:
    """Test cases for create_llm_client function"""

    @patch(LLM_CLASS_PATH)  # Patch the original LLM class import
    def test_init_with_default_config(self, mock_llm_class):
        """Verify initialization with default configuration"""
        # Setup mock
        mock_instance = MagicMock()
        mock_llm_class.return_value = mock_instance

        # Execute
        result = LLMService.get_client()

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
        result = LLMService.get_client(config=custom_config)

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
        assert isinstance(LLMService.get_client(), MagicMock)
