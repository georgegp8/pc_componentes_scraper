"""
Store-specific scrapers package
Each store has its own scraper class optimized for its HTML structure
"""

from .sercoplus_scraper import SercoPlusScraper
from .memorykings_scraper import MemoryKingsScraper
from .pcimpacto_scraper import PCImpactoScraper
from .computershop_scraper import ComputerShopScraper
from .base_scraper import BaseScraper

__all__ = [
    'BaseScraper',
    'SercoPlusScraper',
    'MemoryKingsScraper',
    'PCImpactoScraper',
    'ComputerShopScraper'
]
