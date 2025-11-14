"""
Configuration Management
Loads and manages application configuration
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""
    
    # Database
    DATABASE_PATH: str = os.getenv('DATABASE_PATH', 'pc_prices.db')
    
    # API
    API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
    API_PORT: int = int(os.getenv('API_PORT', '8000'))
    API_RELOAD: bool = os.getenv('API_RELOAD', 'True').lower() == 'true'
    
    # Scraping
    DEFAULT_SCRAPE_FREQUENCY_HOURS: int = int(os.getenv('DEFAULT_SCRAPE_FREQUENCY_HOURS', '24'))
    MAX_CONCURRENT_SCRAPES: int = int(os.getenv('MAX_CONCURRENT_SCRAPES', '3'))
    REQUEST_DELAY_SECONDS: int = int(os.getenv('REQUEST_DELAY_SECONDS', '2'))
    REQUEST_TIMEOUT_SECONDS: int = int(os.getenv('REQUEST_TIMEOUT_SECONDS', '10'))
    
    # Product Matching
    SIMILARITY_THRESHOLD: float = float(os.getenv('SIMILARITY_THRESHOLD', '0.75'))
    AUTO_MATCH_ON_INSERT: bool = os.getenv('AUTO_MATCH_ON_INSERT', 'False').lower() == 'true'
    
    # Scheduler
    ENABLE_AUTO_SCRAPING: bool = os.getenv('ENABLE_AUTO_SCRAPING', 'True').lower() == 'true'
    SCHEDULER_CHECK_INTERVAL_MINUTES: int = int(os.getenv('SCHEDULER_CHECK_INTERVAL_MINUTES', '60'))
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', 'logs/scraper.log')
    
    @classmethod
    def get_store_urls(cls, store_name: str) -> Dict[str, str]:
        """Gets configured URLs for a specific store"""
        prefix = store_name.upper().replace(' ', '')
        urls = {}
        
        for key, value in os.environ.items():
            if key.startswith(prefix + '_'):
                category = key[len(prefix)+1:].lower()
                urls[category] = value
        
        return urls
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Returns configuration as dictionary"""
        return {
            'database_path': cls.DATABASE_PATH,
            'api_host': cls.API_HOST,
            'api_port': cls.API_PORT,
            'scrape_frequency_hours': cls.DEFAULT_SCRAPE_FREQUENCY_HOURS,
            'similarity_threshold': cls.SIMILARITY_THRESHOLD,
            'auto_scraping_enabled': cls.ENABLE_AUTO_SCRAPING
        }


config = Config()
