"""
Security module.

This module provides security-related functionality including code validation
and security best practices enforcement.
"""

from taskguard.security.validator import SecurityValidator, SecurityIssue, SecurityLevel
from taskguard.security.scanner import SecurityScanner
from taskguard.security.patterns import (
    INSECURE_FUNCTIONS,
    DANGEROUS_IMPORTS,
    SHELL_INJECTION_PATTERNS,
    HARDCODED_SECRETS_PATTERNS
)

__all__ = [
    'SecurityValidator',
    'SecurityScanner',
    'SecurityIssue',
    'SecurityLevel',
    'INSECURE_FUNCTIONS',
    'DANGEROUS_IMPORTS',
    'SHELL_INJECTION_PATTERNS',
    'HARDCODED_SECRETS_PATTERNS'
]
