"""
ComputerShop Scraper
Wrapper for easy import from main API
"""

import sys
import os

# Add scrapers directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from computershop.scraper import ComputerShopScraper

__all__ = ['ComputerShopScraper']
