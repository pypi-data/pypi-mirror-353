"""
LLM Interface module.

This module defines the interface for LLM providers.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

@dataclass
class LLMResponse:
    """Container for LLM response data."""
    text: str
    model: str
    tokens_used: int
    finish_reason: str
    raw_response: Optional[Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            'text': self.text,
            'model': self.model,
            'tokens_used': self.tokens_used,
            'finish_reason': self.finish_reason
        }

class LLMInterface(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate text from a prompt.
        
        Args:
            prompt: The prompt to generate text from
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 2.0)
            **kwargs: Additional model-specific parameters
            
        Returns:
            LLMResponse: The generated response
        """
        pass
    
    @abstractmethod
    async def analyze_code(
        self,
        file_path: Union[str, Path],
        task_context: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Analyze code and provide feedback.
        
        Args:
            file_path: Path to the code file to analyze
            task_context: Optional context about the current task
            **kwargs: Additional analysis parameters
            
        Returns:
            Dict containing analysis results
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models.
        
        Returns:
            List of model names
        """
        pass
    
    @abstractmethod
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model.
        
        Args:
            model_name: Name of the model to get info for
            
        Returns:
            Dict containing model information
        """
        pass
