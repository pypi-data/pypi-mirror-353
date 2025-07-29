"""
Security Scanner module.

This module provides functionality to scan directories and files for security issues.
"""
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Pattern
import fnmatch

from .validator import SecurityValidator, SecurityIssue, SecurityLevel

logger = logging.getLogger(__name__)

class SecurityScanner:
    """Scans directories and files for security issues."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the security scanner.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.validator = SecurityValidator(config)
        self.exclude_dirs = set(self.config.get('exclude_dirs', ['.git', '__pycache__', 'venv', 'env', 'node_modules']))
        self.exclude_files = set(self.config.get('exclude_files', ['*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll']))
    
    def scan_directory(self, directory: str) -> Dict[str, List[Dict[str, Any]]]:
        """Scan a directory for security issues.
        
        Args:
            directory: Path to the directory to scan
            
        Returns:
            Dictionary mapping file paths to lists of security issues
        """
        results = {}
        directory_path = Path(directory).resolve()
        
        if not directory_path.exists() or not directory_path.is_dir():
            logger.error(f"Directory not found: {directory}")
            return results
        
        for root, dirs, files in os.walk(directory_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                
                # Skip excluded files
                if any(fnmatch.fnmatch(file, pattern) for pattern in self.exclude_files):
                    continue
                
                # Only scan Python files by default, can be configured
                if file_path.suffix == '.py' or self._should_scan_file(file_path):
                    issues = self.validator.validate_file(file_path)
                    if issues:
                        results[str(file_path)] = [issue.to_dict() for issue in issues]
        
        return results
    
    def scan_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Scan a single file for security issues.
        
        Args:
            file_path: Path to the file to scan
            
        Returns:
            List of security issues found in the file
        """
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            logger.error(f"File not found: {file_path}")
            return []
        
        issues = self.validator.validate_file(path)
        return [issue.to_dict() for issue in issues]
    
    def _should_scan_file(self, file_path: Path) -> bool:
        """Determine if a file should be scanned based on configuration.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if the file should be scanned, False otherwise
        """
        # By default, only scan Python files
        if file_path.suffix == '.py':
            return True
            
        # Check file extensions in config
        if 'scan_extensions' in self.config:
            return file_path.suffix.lower() in self.config['scan_extensions']
            
        # Check file patterns in config
        if 'scan_patterns' in self.config:
            return any(fnmatch.fnmatch(file_path.name, pattern) 
                      for pattern in self.config['scan_patterns'])
        
        return False
