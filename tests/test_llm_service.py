import os
import sys
import unittest

from crewai import LLM
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# sys.path.append(str(Path(__file__).parent.parent))
from src.services.llm.llm_config import LLMConfig
from src.services.llm.llm_service import LLMService

LLM_CLASS_PATH = "src.services.llm.llm_config.LLM"  # Update this to actual import path

class TestLLMService(unittest.TestCase):
    def setUp(self):
        self.service = LLMService()
        self.valid_config = {
            "provider": "openai",
            "model": "gpt-4",
            "base_url": "https://api.openai.com/v1",
            "api_key": "test_key",
            "temperature": 0.7,
            "max_tokens": 1000,
            "timeout": 30
        }
        self.invalid_config = {
            "provider": "invalid/provider", 
            "base_url": "invalid_url"
        }

    def test_get_client_with_default_config(self):
        with patch('src.services.llm.llm_service.get_llm_config') as mock_get_config:
            mock_config = MagicMock(spec=LLMConfig)
            mock_config.provider = "default"
            mock_config.model = "default-model"
            mock_get_config.return_value = mock_config

            with patch.object(self.service, '_create_client') as mock_create:
                mock_client = MagicMock(spec=LLM)
                mock_create.return_value = mock_client

                client = self.service.get_client()
                cached_client = self.service.get_client()

                mock_get_config.assert_called_once()
                mock_create.assert_called_once()
                self.assertEqual(client, cached_client)
                self.assertEqual(mock_create.call_args[0][0], mock_config)

