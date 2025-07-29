"""
LLM Provider implementations.

This module contains implementations of various LLM providers.
"""
import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

import requests
from pydantic import BaseModel, Field, HttpUrl

from taskguard.llm.interface import LLMInterface, LLMResponse

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """Base class for LLM providers."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize the LLM provider.
        
        Args:
            api_key: API key for the provider
            base_url: Base URL for the API (if self-hosted)
        """
        self.api_key = api_key or os.getenv(f"{self.__class__.__name__.upper()}_API_KEY")
        self.base_url = base_url
        self._models = []
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate text from a prompt.
        
        Args:
            prompt: The prompt to generate text from
            model: The model to use for generation
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 2.0)
            **kwargs: Additional model-specific parameters
            
        Returns:
            LLMResponse: The generated response
        """
        pass
    
    @abstractmethod
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models.
        
        Returns:
            List of model information dictionaries
        """
        pass

class OllamaProvider(LLMProvider):
    """Ollama LLM provider implementation."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """Initialize the Ollama provider.
        
        Args:
            base_url: Base URL for the Ollama API
        """
        super().__init__(base_url=base_url)
        self.base_url = base_url.rstrip('/')
    
    async def generate(
        self,
        prompt: str,
        model: str = "llama2",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate text using Ollama API."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            return LLMResponse(
                text=data.get('response', ''),
                model=model,
                tokens_used=data.get('eval_count', 0),
                finish_reason=data.get('done_reason', 'stop'),
                raw_response=data
            )
        except Exception as e:
            logger.error(f"Error generating text with Ollama: {e}")
            raise
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available Ollama models."""
        url = f"{self.base_url}/api/tags"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('models', [])
        except Exception as e:
            logger.error(f"Error listing Ollama models: {e}")
            return []

class OpenAIModel(LLMProvider):
    """OpenAI model implementation."""
    
    BASE_URL = "https://api.openai.com/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenAI provider.
        
        Args:
            api_key: OpenAI API key
        """
        super().__init__(api_key=api_key)
        self.base_url = self.BASE_URL
    
    async def generate(
        self,
        prompt: str,
        model: str = "gpt-3.5-turbo",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate text using OpenAI API."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            return LLMResponse(
                text=data['choices'][0]['message']['content'],
                model=model,
                tokens_used=data['usage']['total_tokens'],
                finish_reason=data['choices'][0]['finish_reason'],
                raw_response=data
            )
        except Exception as e:
            logger.error(f"Error generating text with OpenAI: {e}")
            raise
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available OpenAI models."""
        url = f"{self.base_url}/models"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('data', [])
        except Exception as e:
            logger.error(f"Error listing OpenAI models: {e}")
            return []

class AnthropicModel(LLMProvider):
    """Anthropic model implementation."""
    
    BASE_URL = "https://api.anthropic.com/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Anthropic provider.
        
        Args:
            api_key: Anthropic API key
        """
        super().__init__(api_key=api_key)
        self.base_url = self.BASE_URL
    
    async def generate(
        self,
        prompt: str,
        model: str = "claude-2",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate text using Anthropic API."""
        url = f"{self.base_url}/complete"
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
            "max_tokens_to_sample": max_tokens,
            "temperature": temperature,
            **kwargs
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            return LLMResponse(
                text=data.get('completion', ''),
                model=model,
                tokens_used=len(data.get('completion', '').split()),
                finish_reason=data.get('stop_reason', 'stop'),
                raw_response=data
            )
        except Exception as e:
            logger.error(f"Error generating text with Anthropic: {e}")
            raise
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available Anthropic models."""
        # Anthropic doesn't have a models endpoint, return known models
        return [
            {"id": "claude-2", "name": "Claude 2"},
            {"id": "claude-instant-1", "name": "Claude Instant"}
        ]
