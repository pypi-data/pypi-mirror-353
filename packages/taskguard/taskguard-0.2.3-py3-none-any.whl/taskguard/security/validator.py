"""
Security Validator module.

This module provides functionality to validate code against security best practices.
"""

import ast
import logging
import re
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern, Set

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security issue severity levels."""

    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


@dataclass
class SecurityIssue:
    """Represents a security issue found during validation."""

    level: SecurityLevel
    message: str
    line: Optional[int] = None
    column: Optional[int] = None
    code_snippet: Optional[str] = None
    fix_suggestion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "level": self.level.name,
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "code_snippet": self.code_snippet,
            "fix_suggestion": self.fix_suggestion,
        }


class SecurityValidator:
    """Validates code against security best practices."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the security validator.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.issues: List[SecurityIssue] = []

    def validate_file(self, file_path: Path) -> List[SecurityIssue]:
        """Validate a file for security issues.

        Args:
            file_path: Path to the file to validate

        Returns:
            List of security issues found
        """
        self.issues = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for insecure patterns
            self._check_insecure_patterns(content, file_path)

            # Parse AST for deeper analysis
            try:
                tree = ast.parse(content)
                self._analyze_ast(tree, file_path)
            except SyntaxError as e:
                self.issues.append(
                    SecurityIssue(
                        level=SecurityLevel.HIGH,
                        message=f"Syntax error in file: {e.msg}",
                        line=e.lineno,
                        column=e.offset,
                        code_snippet=(
                            content.split("\n")[e.lineno - 1] if e.lineno else None
                        ),
                    )
                )

        except Exception as e:
            logger.error(f"Error validating file {file_path}: {e}")
            self.issues.append(
                SecurityIssue(
                    level=SecurityLevel.HIGH,
                    message=f"Error validating file: {str(e)}",
                    code_snippet=str(e),
                )
            )

        return self.issues

    def _check_insecure_patterns(self, content: str, file_path: Path) -> None:
        """Check for insecure patterns in the content."""
        from .patterns import (
            DANGEROUS_IMPORTS,
            HARDCODED_SECRETS_PATTERNS,
            INSECURE_FUNCTIONS,
            SHELL_INJECTION_PATTERNS,
        )

        lines = content.split("\n")

        # Check for dangerous imports
        for i, line in enumerate(lines, 1):
            for pattern in DANGEROUS_IMPORTS:
                if re.search(pattern, line):
                    self.issues.append(
                        SecurityIssue(
                            level=SecurityLevel.HIGH,
                            message=f"Dangerous import detected: {line.strip()}",
                            line=i,
                            code_snippet=line,
                            fix_suggestion=f"Avoid using {line.strip()}, use safer alternatives",
                        )
                    )

        # Check for insecure function calls
        for i, line in enumerate(lines, 1):
            for func in INSECURE_FUNCTIONS:
                if func in line and not line.strip().startswith("#"):
                    self.issues.append(
                        SecurityIssue(
                            level=SecurityLevel.HIGH,
                            message=f"Insecure function call: {func}",
                            line=i,
                            code_snippet=line,
                            fix_suggestion=f"Replace {func} with a safer alternative",
                        )
                    )

        # Check for shell injection patterns
        for i, line in enumerate(lines, 1):
            for pattern in SHELL_INJECTION_PATTERNS:
                if re.search(pattern, line):
                    self.issues.append(
                        SecurityIssue(
                            level=SecurityLevel.CRITICAL,
                            message="Potential shell injection vulnerability",
                            line=i,
                            code_snippet=line,
                            fix_suggestion="Use subprocess with shell=False or use shlex.quote() for shell=True",
                        )
                    )

        # Check for hardcoded secrets
        for i, line in enumerate(lines, 1):
            for pattern in HARDCODED_SECRETS_PATTERNS:
                if re.search(pattern, line):
                    self.issues.append(
                        SecurityIssue(
                            level=SecurityLevel.HIGH,
                            message="Potential hardcoded secret detected",
                            line=i,
                            code_snippet=line,
                            fix_suggestion="Store secrets in environment variables or a secure secret manager",
                        )
                    )

    def _analyze_ast(self, tree: ast.AST, file_path: Path) -> None:
        """Analyze the AST for security issues."""
        analyzer = SecurityASTAnalyzer()
        analyzer.visit(tree)
        self.issues.extend(analyzer.issues)


class SecurityASTAnalyzer(ast.NodeVisitor):
    """AST analyzer for security issues."""

    def __init__(self):
        self.issues: List[SecurityIssue] = []

    def visit_Call(self, node: ast.Call) -> None:
        """Visit function calls."""
        # Check for dangerous function calls
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in ["eval", "exec", "execfile"]:
                self.issues.append(
                    SecurityIssue(
                        level=SecurityLevel.CRITICAL,
                        message=f"Use of dangerous function: {func_name}",
                        line=node.lineno,
                        col_offset=node.col_offset,
                        fix_suggestion=f"Avoid using {func_name}, consider safer alternatives",
                    )
                )

        # Check for shell=True in subprocess calls
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr in ["Popen", "run", "call"]
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "subprocess"
        ):

            for kw in node.keywords:
                if (
                    kw.arg == "shell"
                    and isinstance(kw.value, ast.Constant)
                    and kw.value.value is True
                ):
                    self.issues.append(
                        SecurityIssue(
                            level=SecurityLevel.HIGH,
                            message="Potential shell injection with shell=True",
                            line=node.lineno,
                            col_offset=node.col_offset,
                            fix_suggestion="Avoid shell=True when possible, or use shlex.quote() on arguments",
                        )
                    )

        self.generic_visit(node)
