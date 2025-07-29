"""
Security patterns module.

This module contains regular expressions and patterns for detecting security issues.
"""

import re

# Dangerous Python functions that should be avoided
INSECURE_FUNCTIONS = [
    "eval",
    "exec",
    "execfile",
    "compile",
    "os.system",
    "os.popen",
    "os.popen2",
    "os.popen3",
    "os.popen4",
    "os.execl",
    "os.execle",
    "os.execlp",
    "os.execlpe",
    "os.execv",
    "os.execve",
    "os.execvp",
    "os.execvpe",
    "os.spawnl",
    "os.spawnle",
    "os.spawnlp",
    "os.spawnlpe",
    "os.spawnv",
    "os.spawnve",
    "os.spawnvp",
    "os.spawnvpe",
    "os.startfile",
    "pickle.load",
    "pickle.loads",
    "cPickle.load",
    "cPickle.loads",
    "subprocess.call",
    "subprocess.check_call",
    "subprocess.check_output",
    "subprocess.Popen",
    "subprocess.run",
    "pickle.Unpickler",
    "cPickle.Unpickler",
    "marshal.load",
    "marshal.loads",
    "yaml.load",
    "yaml.unsafe_load",
    "yaml.full_load",
    "pickletools.optimize",
]

# Dangerous imports that should be avoided
DANGEROUS_IMPORTS = [
    r"^\s*import\s+os\s*$",
    r"^\s*from\s+os\s+import",
    r"^\s*import\s+subprocess\s*$",
    r"^\s*from\s+subprocess\s+import",
    r"^\s*import\s+pickle\s*$",
    r"^\s*from\s+pickle\s+import",
    r"^\s*import\s+cPickle\s*$",
    r"^\s*from\s+cPickle\s+import",
    r"^\s*import\s+shell\s*$",
    r"^\s*from\s+shell\s+import",
    r"^\s*import\s+commands\s*$",
    r"^\s*from\s+commands\s+import",
    r"^\s*import\s+pty\s*$",
    r"^\s*from\s+pty\s+import",
    r"^\s*import\s+shlex\s*$",
    r"^\s*from\s+shlex\s+import",
]

# Patterns that might indicate shell injection
SHELL_INJECTION_PATTERNS = [
    # Shell metacharacters in potentially vulnerable functions
    r"os\.system\([^)]*[;&|`]",
    r"subprocess\.(call|check_call|check_output|run|Popen)\([^)]*shell\s*=\s*True[^)]*[;&|`]",
    # Command chaining
    r"[;&|`]",
    # Command substitution
    r"\$\([^)]*\)",
    r"`[^`]*`",
    # Redirection
    r"[><]",
    # Pipes
    r"\|",
    # Background processes
    r"&",
]

# Patterns that might indicate hardcoded secrets
HARDCODED_SECRETS_PATTERNS = [
    # API keys
    r'(?i)api[_-]?key\s*[=:]\s*["\'][\w-]{20,}["\']',
    # Passwords
    r'(?i)password\s*[=:]\s*["\'][^"\']+["\']',
    # Secret keys
    r'(?i)secret[_-]?key\s*[=:]\s*["\'][\w-]{20,}["\']',
    # Bearer tokens
    r"bearer\s+[\w-]{20,}",
    # OAuth tokens
    r'oauth[\w-]*\s*[=:]\s*["\'][\w-]{20,}["\']',
    # AWS credentials
    r'aws[_-]?(?:access[_-]?key[_-]?id|secret[_-]?access[_-]?key|session[_-]?token)\s*[=:]\s*["\'][\w-]{20,}["\']',
    # Database URIs
    r"(?i)(?:postgres|postgresql|mysql|mongodb|redis)://[\w-]+:[^@\s]+@",
]

# Patterns for SQL injection detection
SQL_INJECTION_PATTERNS = [
    # String concatenation in SQL queries
    r'"[^"]*\s*\+\s*[^\s"]*sql',
    r'"[^"]*\s*%\s*[^\s"]*sql',
    r'"[^"]*\s*\{\s*[^\s"]*\s*\}\s*[^\s"]*sql',
    # Raw SQL with format or % formatting
    r'cursor\.(execute|executemany|callproc|executescript)\s*\(\s*f?["\']',
    # Direct string formatting in SQL
    r"SELECT\s+\*\s+FROM\s+\w+\s+WHERE\s+[^;]+\s*%\s*\(",
    r"SELECT\s+\*\s+FROM\s+\w+\s+WHERE\s+[^;]+\s*\+\s*",
]

# Patterns for potential XSS (Cross-Site Scripting) issues
XSS_PATTERNS = [
    # Unsafe HTML output
    r"<\s*\/?\s*(?:script|iframe|object|embed|applet|form|input|button|select|textarea|style|link|meta|base|frame|frameset)",
    # Unsafe JavaScript event handlers
    r"on(?:load|click|dblclick|mousedown|mouseup|mousemove|mouseout|mouseover|mouseenter|mouseleave|keydown|keyup|keypress|submit|reset|focus|blur|change|select|error)",
    # JavaScript protocol in URLs
    r"javascript:",
    # Data URIs that might contain scripts
    r"data:\s*text\/(?:html|javascript|vbscript)",
]

# Compiled patterns for better performance
COMPILED_PATTERNS = {
    "insecure_functions": [
        re.compile(rf"\b{re.escape(func)}\s*\(") for func in INSECURE_FUNCTIONS
    ],
    "dangerous_imports": [re.compile(pattern) for pattern in DANGEROUS_IMPORTS],
    "shell_injection": [re.compile(pattern) for pattern in SHELL_INJECTION_PATTERNS],
    "hardcoded_secrets": [
        re.compile(pattern, re.IGNORECASE) for pattern in HARDCODED_SECRETS_PATTERNS
    ],
    "sql_injection": [
        re.compile(pattern, re.IGNORECASE) for pattern in SQL_INJECTION_PATTERNS
    ],
    "xss": [re.compile(pattern, re.IGNORECASE) for pattern in XSS_PATTERNS],
}
