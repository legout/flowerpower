"""
Custom exceptions for the cfg module.
"""

from typing import Any, Dict, Optional


class ConfigError(Exception):
    """Base exception for configuration-related errors."""
    pass


class ConfigLoadError(ConfigError):
    """Exception raised when configuration loading fails."""
    
    def __init__(self, message: str, path: Optional[str] = None, original_error: Optional[Exception] = None):
        self.path = path
        self.original_error = original_error
        super().__init__(message)


class ConfigSaveError(ConfigError):
    """Exception raised when configuration saving fails."""
    
    def __init__(self, message: str, path: Optional[str] = None, original_error: Optional[Exception] = None):
        self.path = path
        self.original_error = original_error
        super().__init__(message)


class ConfigValidationError(ConfigError):
    """Exception raised when configuration validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        self.field = field
        self.value = value
        super().__init__(message)


class ConfigSecurityError(ConfigError):
    """Exception raised for security-related configuration errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.details = details or {}
        super().__init__(message)


class ConfigPathError(ConfigSecurityError):
    """Exception raised for path-related security errors."""
    
    def __init__(self, message: str, path: Optional[str] = None):
        super().__init__(message, {"path": path})
        self.path = path