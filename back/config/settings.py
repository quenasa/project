"""
Application configuration settings
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    # Flask settings
    JSON_SORT_KEYS = False
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'
    PORT = int(os.getenv('PORT', 5000))
    HOST = os.getenv('HOST', '0.0.0.0')
    
    # Cache settings
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 3600  # 1 hour
    
    # Rate limiting settings
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    
    # API Keys and URLs
    # Copernicus Climate Data Store (CDS)
    COPERNICUS_API_KEY = os.getenv('COPERNICUS_API_KEY', '')
    COPERNICUS_API_URL = os.getenv('COPERNICUS_API_URL', 'https://cds.climate.copernicus.eu/api/v2')
    
    # WorldPop - Spatial Data Infrastructure
    WORLDPOP_API_URL = os.getenv('WORLDPOP_API_URL', 'https://www.worldpop.org/sdi/api')
    
    # Geographic focus
    TARGET_REGION = 'africa'  # Enfoque en África


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    CACHE_TYPE = 'null'  # Disable cache for tests


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
