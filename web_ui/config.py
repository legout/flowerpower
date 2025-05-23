"""
Configuration settings for FlowerPower Web UI
"""

import os
from typing import Dict, Any

class Config:
    """Base configuration class"""
    
    # Server settings
    HOST = os.getenv("FLOWERPOWER_WEB_HOST", "0.0.0.0")
    PORT = int(os.getenv("FLOWERPOWER_WEB_PORT", "8000"))
    DEBUG = os.getenv("FLOWERPOWER_WEB_DEBUG", "true").lower() == "true"
    
    # Application settings
    APP_NAME = "FlowerPowerWeb"
    VERSION = "1.0.0"
    
    # CORS settings
    CORS_ORIGINS = os.getenv("FLOWERPOWER_WEB_CORS_ORIGINS", "*")
    
    # Static files
    STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
    
    # Database settings (for future use)
    DATABASE_URL = os.getenv("FLOWERPOWER_DATABASE_URL", "sqlite:///flowerpower.db")
    
    # Security settings
    SECRET_KEY = os.getenv("FLOWERPOWER_SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Datastar settings
    DATASTAR_STREAM_ENDPOINT = "/datastar/stream"
    
    # Pagination settings
    PROJECTS_PER_PAGE = int(os.getenv("FLOWERPOWER_PROJECTS_PER_PAGE", "10"))
    
    @classmethod
    def get_settings(cls) -> Dict[str, Any]:
        """Get all configuration settings as a dictionary"""
        return {
            key: getattr(cls, key)
            for key in dir(cls)
            if not key.startswith('_') and not callable(getattr(cls, key))
        }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    HOST = "127.0.0.1"

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SECRET_KEY = os.getenv("FLOWERPOWER_SECRET_KEY")
    
    @classmethod
    def validate(cls):
        """Validate production configuration"""
        if not os.getenv("FLOWERPOWER_SECRET_KEY"):
            raise ValueError("FLOWERPOWER_SECRET_KEY environment variable must be set in production")

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    DATABASE_URL = "sqlite:///:memory:"

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name: str = None) -> Config:
    """Get configuration class based on environment"""
    if config_name is None:
        config_name = os.getenv('FLOWERPOWER_WEB_ENV', 'default')
    
    return config.get(config_name, DevelopmentConfig)