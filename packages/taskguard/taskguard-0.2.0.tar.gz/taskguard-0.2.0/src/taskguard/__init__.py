#!/usr/bin/env python3
"""
🧠 TaskGuard - LLM Task Controller with Local AI Intelligence

A comprehensive task management system that controls LLM behavior,
enforces best practices, and maintains focus through intelligent automation.

Features:
- 🎯 Focus control and task management
- 🛡️ Safety checking and dangerous command blocking
- 📚 Best practices enforcement
- 🧠 Local AI intelligence for document parsing
- 📊 Productivity analytics and insights
- 🔄 Universal document format support

Example usage:
    >>> from taskguard import TaskController
    >>> controller = TaskController()
    >>> controller.start_task(1)
    >>> controller.check_best_practices("myfile.py")
"""

__version__ = "0.2.0"
__author__ = "Tom Sapletta"
__email__ = "info@softreck.dev"
__license__ = "Apache-2.0"
__description__ = "🧠 LLM Task Controller with Local AI Intelligence"

# Core imports
from .taskguard import LLMTaskController as TaskController
from .local_llm_interface import LocalLLMInterface, IntelligentDocumentParser
from .cli import main as cli_main

# Version info
VERSION_INFO = {
    "major": 0,
    "minor": 2,
    "patch": 0,
    "release": "beta",
    "build": "20241205"
}

# Feature flags
FEATURES = {
    "local_llm": True,
    "document_parsing": True,
    "best_practices": True,
    "shell_integration": True,
    "productivity_analytics": True,
    "safety_checking": True,
    "focus_control": True,
}

# Supported file formats
SUPPORTED_FORMATS = {
    "todo": ["markdown", "yaml", "plain_text", "org_mode", "json"],
    "changelog": ["markdown", "keep_a_changelog", "conventional", "plain_text"],
    "config": ["yaml", "json", "toml"],
}

# Supported LLM providers
SUPPORTED_LLM_PROVIDERS = [
    "ollama",
    "lmstudio",
    "openai_compatible",
    "anthropic",
    "openai",
]

# Default configuration
DEFAULT_CONFIG = {
    "focus": {
        "max_files_per_task": 3,
        "require_todo_completion": True,
        "task_timeout_minutes": 30,
    },
    "local_llm": {
        "provider": "ollama",
        "model": "llama3.2:3b",
        "base_url": "http://localhost:11434",
    },
    "best_practices": {
        "python": {
            "enforce_docstrings": True,
            "enforce_type_hints": True,
            "max_function_length": 50,
        }
    }
}

# Public API
__all__ = [
    # Core classes
    "TaskController",
    "LocalLLMInterface",
    "IntelligentDocumentParser",

    # CLI
    "cli_main",

    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__description__",

    # Configuration
    "VERSION_INFO",
    "FEATURES",
    "SUPPORTED_FORMATS",
    "SUPPORTED_LLM_PROVIDERS",
    "DEFAULT_CONFIG",
]


def get_version() -> str:
    """Get the current version string."""
    return __version__


def get_version_info() -> dict:
    """Get detailed version information."""
    return VERSION_INFO.copy()


def check_features() -> dict:
    """Check which features are available."""
    available_features = FEATURES.copy()

    # Check for optional dependencies
    try:
        import requests
        available_features["http_requests"] = True
    except ImportError:
        available_features["http_requests"] = False

    try:
        import yaml
        available_features["yaml_support"] = True
    except ImportError:
        available_features["yaml_support"] = False

    return available_features


def create_controller(**kwargs) -> TaskController:
    """
    Create a TaskController instance with optional configuration.

    Args:
        **kwargs: Configuration options to override defaults

    Returns:
        TaskController: Configured task controller instance

    Example:
        >>> controller = create_controller(
        ...     focus={'max_files_per_task': 5},
        ...     local_llm={'provider': 'lmstudio'}
        ... )
    """
    return TaskController(**kwargs)


# Package-level convenience functions
def quick_start():
    """Quick start guide for new users."""
    print("🚀 TaskGuard Quick Start")
    print("=" * 30)
    print("1. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
    print("2. Start Ollama: ollama serve")
    print("3. Pull model: ollama pull llama3.2:3b")
    print("4. Initialize: python -c 'import taskguard; taskguard.cli_main()'")
    print("5. Activate: source ~/.llmtask_shell.sh")
    print("6. Start working: show_tasks")


def system_info():
    """Display system and package information."""
    import sys
    import platform

    print("🧠 TaskGuard System Information")
    print("=" * 35)
    print(f"TaskGuard Version: {__version__}")
    print(f"Python Version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()[0]}")

    features = check_features()
    print("\n🔧 Available Features:")
    for feature, available in features.items():
        status = "✅" if available else "❌"
        print(f"   {status} {feature}")

    print(f"\n📊 Supported Formats:")
    for format_type, formats in SUPPORTED_FORMATS.items():
        print(f"   {format_type}: {', '.join(formats)}")


# Error classes
class TaskGuardError(Exception):
    """Base exception for TaskGuard."""
    pass


class ConfigurationError(TaskGuardError):
    """Configuration-related errors."""
    pass


class LLMConnectionError(TaskGuardError):
    """LLM connection errors."""
    pass


class DocumentParsingError(TaskGuardError):
    """Document parsing errors."""
    pass


class BestPracticeViolation(TaskGuardError):
    """Best practice violations."""
    pass


# Add error classes to public API
__all__.extend([
    "TaskGuardError",
    "ConfigurationError",
    "LLMConnectionError",
    "DocumentParsingError",
    "BestPracticeViolation",
    "quick_start",
    "system_info",
    "get_version",
    "get_version_info",
    "check_features",
    "create_controller",
])

# Development mode checks
if __name__ == "__main__":
    system_info()
    print("\n" + "=" * 50)
    quick_start()