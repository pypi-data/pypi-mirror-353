"""
Security module.

This module provides security-related functionality including code validation
and security best practices enforcement.
"""

from taskguard.security.patterns import (
    DANGEROUS_IMPORTS,
    HARDCODED_SECRETS_PATTERNS,
    INSECURE_FUNCTIONS,
    SHELL_INJECTION_PATTERNS,
)
from taskguard.security.scanner import SecurityScanner
from taskguard.security.validator import SecurityIssue, SecurityLevel, SecurityValidator

__all__ = [
    "SecurityValidator",
    "SecurityScanner",
    "SecurityIssue",
    "SecurityLevel",
    "INSECURE_FUNCTIONS",
    "DANGEROUS_IMPORTS",
    "SHELL_INJECTION_PATTERNS",
    "HARDCODED_SECRETS_PATTERNS",
]
