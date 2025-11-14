"""
Base Scraper Class
Abstract base class for all store-specific scrapers
"""

import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
from abc import ABC, abstractmethod
import time


class BaseScraper(ABC):
    """Base class for all PC component scrapers"""
    
    def __init__(self, store_name: str, use_selenium: bool = False):
        self.store_name = store_name
        self.use_selenium = use_selenium
        self.driver = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def init_selenium(self):
        """Initialize Selenium WebDriver using built-in Chrome driver manager"""
        if self.driver:
            return
        
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            chrome_options = Options()
            chrome_options.add_argument('--headless=new')  # New headless mode
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument(f'user-agent={self.headers["User-Agent"]}')
            
            # Selenium 4.6+ downloads ChromeDriver automatically
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✅ Selenium WebDriver iniciado con ChromeDriver automático")
            
        except Exception as e:
            print(f"⚠️ Error iniciando Selenium: {e}")
            print("   Continuando con requests...")
            self.use_selenium = False
    
    def close_selenium(self):
        """Close Selenium WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                print("✅ Selenium WebDriver cerrado")
            except:
                pass
    
    def __del__(self):
        """Destructor to ensure Selenium is closed"""
        self.close_selenium()
        
    @abstractmethod
    def scrape_product_page(self, url: str) -> Optional[Dict]:
        """
        Scrapes a single product page
        Must be implemented by each store-specific scraper
        """
        pass
    
    @abstractmethod
    def scrape_category_page(self, url: str) -> List[Dict]:
        """
        Scrapes a category/listing page
        Must be implemented by each store-specific scraper
        """
        pass
    
    def fetch_page(self, url: str, timeout: int = 10, wait_time: int = 3) -> Optional[BeautifulSoup]:
        """
        Fetches a page and returns BeautifulSoup object
        
        Args:
            url: URL to fetch
            timeout: Request timeout in seconds
            wait_time: Time to wait for JavaScript to load (Selenium only)
            
        Returns:
            BeautifulSoup object or None if error
        """
        if self.use_selenium:
            return self._fetch_with_selenium(url, wait_time)
        else:
            return self._fetch_with_requests(url, timeout)
    
    def _fetch_with_requests(self, url: str, timeout: int = 10) -> Optional[BeautifulSoup]:
        """Fetch page using requests library"""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            
            return BeautifulSoup(response.content, 'html.parser')
            
        except requests.RequestException as e:
            print(f"❌ Error fetching {url}: {e}")
            return None
    
    def _fetch_with_selenium(self, url: str, wait_time: int = 3) -> Optional[BeautifulSoup]:
        """Fetch page using Selenium (for JavaScript-heavy sites)"""
        try:
            if not self.driver:
                self.init_selenium()
            
            if not self.driver:
                return self._fetch_with_requests(url)
            
            self.driver.get(url)
            time.sleep(wait_time)  # Wait for JavaScript to load
            
            page_source = self.driver.page_source
            return BeautifulSoup(page_source, 'html.parser')
            
        except Exception as e:
            print(f"❌ Error fetching with Selenium {url}: {e}")
            return None
    
    def _normalize_price_number(self, price_str: str) -> str:
        """
        Normalize price number from various formats to standard float string
        
        Examples:
            "1.953,67" -> "1953.67" (European format with thousands separator)
            "1,953.67" -> "1953.67" (US format with thousands separator)
            "1 326.49" -> "1326.49" (Space as thousands separator)
            "91,80" -> "91.80" (European format without thousands)
            "91.80" -> "91.80" (US format without thousands)
        """
        # Check if spaces are used as thousands separators (e.g., "1 326.49")
        # This happens when there are spaces AND a dot/comma for decimals
        if ' ' in price_str or '\xa0' in price_str:
            # Count dots and commas before removing spaces
            has_dot = '.' in price_str
            has_comma = ',' in price_str
            
            # If there's a space followed by exactly 3 digits and then a decimal separator
            # Example: "1 326.49" or "1 326,49"
            if has_dot or has_comma:
                # Remove spaces - they're thousands separators
                price_str = price_str.replace(' ', '').replace('\xa0', '')
                
                # Now normalize the decimal separator
                if has_comma and not has_dot:
                    # "1326,49" -> "1326.49"
                    price_str = price_str.replace(',', '.')
                elif has_dot and not has_comma:
                    # "1326.49" -> "1326.49" (already correct)
                    pass
                elif has_dot and has_comma:
                    # Check which comes last
                    dot_pos = price_str.rfind('.')
                    comma_pos = price_str.rfind(',')
                    if comma_pos > dot_pos:
                        # "1.326,49" -> "1326.49"
                        price_str = price_str.replace('.', '').replace(',', '.')
                    else:
                        # "1,326.49" -> "1326.49"
                        price_str = price_str.replace(',', '')
                
                return price_str
            else:
                # Just spaces, no decimal - remove them
                price_str = price_str.replace(' ', '').replace('\xa0', '')
        
        # Original logic for other cases
        # Count dots and commas
        dot_count = price_str.count('.')
        comma_count = price_str.count(',')
        
        # Determine format
        if dot_count > 1:
            # Multiple dots = European thousands separator (1.953.456,78)
            price_str = price_str.replace('.', '').replace(',', '.')
        elif comma_count > 1:
            # Multiple commas = unlikely but handle (1,953,456.78)
            price_str = price_str.replace(',', '')
        elif dot_count == 1 and comma_count == 1:
            # Both present - check which is last
            dot_pos = price_str.rfind('.')
            comma_pos = price_str.rfind(',')
            if comma_pos > dot_pos:
                # European format: 1.953,67
                price_str = price_str.replace('.', '').replace(',', '.')
            else:
                # US format: 1,953.67
                price_str = price_str.replace(',', '')
        elif comma_count == 1 and dot_count == 0:
            # Only comma - check if it's decimal or thousands
            comma_pos = price_str.rfind(',')
            after_comma = price_str[comma_pos+1:]
            if len(after_comma) == 2:
                # Likely decimal: 91,80 -> 91.80
                price_str = price_str.replace(',', '.')
            elif len(after_comma) == 3:
                # Likely thousands: 1,000 -> 1000
                price_str = price_str.replace(',', '')
        
        return price_str
    
    def parse_price(self, price_text: str) -> Dict:
        """
        Parses price text to extract USD and local currency
        
        Examples:
            "$91,80 (S/319,46)" -> price_usd: 91.80, price_local: 319.46
            "$131.00 - S/445.40" -> price_usd: 131.00, price_local: 445.40
            "$ 345.00 ó S/ 1,186.50" -> price_usd: 345.00, price_local: 1186.50
            "$ 1.953,67 (S/ 2.444,00)" -> price_usd: 1953.67, price_local: 2444.00
        """
        prices = {}
        
        # Remove extra whitespace
        price_text = re.sub(r'\s+', ' ', price_text.strip())
        
        # Pattern 1: $91,80 (S/319,46) or $ 1.953,67 (S/ 2.444,00)
        pattern1 = r'\$\s*([\d,\.]+)\s*\((?:S/|S\/)\s*([\d,\.]+)\)'
        match = re.search(pattern1, price_text)
        
        if match:
            usd_price = self._normalize_price_number(match.group(1))
            local_price = self._normalize_price_number(match.group(2))
            
            prices['price_usd'] = float(usd_price)
            prices['price_local'] = float(local_price)
            prices['currency'] = 'PEN'
            return prices
        
        # Pattern 2: $131.00 - S/445.40 or $389.00 - S/1 326.49 (with space as thousands separator)
        pattern2 = r'\$\s*([\d,\.]+)\s*-\s*(?:S/|S\/)\s*([\d,\.\s]+)'
        match = re.search(pattern2, price_text)
        
        if match:
            usd_price = self._normalize_price_number(match.group(1))
            local_price = self._normalize_price_number(match.group(2))
            
            prices['price_usd'] = float(usd_price)
            prices['price_local'] = float(local_price)
            prices['currency'] = 'PEN'
            return prices
        
        # Pattern 3: $ 345.00 ó S/ 1,186.50
        pattern3 = r'\$\s*([\d,\.]+)\s*(?:ó|o)\s*(?:S/|S\/)\s*([\d,\.]+)'
        match = re.search(pattern3, price_text)
        
        if match:
            usd_price = match.group(1).replace(',', '')
            local_price = match.group(2).replace(',', '')
            
            prices['price_usd'] = float(usd_price)
            prices['price_local'] = float(local_price)
            prices['currency'] = 'PEN'
            return prices
        
        # Fallback: try to extract just USD price
        usd_match = re.search(r'\$\s*([\d,\.]+)', price_text)
        if usd_match:
            usd_price = usd_match.group(1).replace(',', '')
            prices['price_usd'] = float(usd_price)
            prices['currency'] = 'USD'
            
            # Try to find PEN price
            pen_match = re.search(r'(?:S/|S\/)\s*([\d,\.]+)', price_text)
            if pen_match:
                local_price = pen_match.group(1).replace(',', '')
                prices['price_local'] = float(local_price)
                prices['currency'] = 'PEN'
        
        return prices
    
    def parse_stock(self, stock_text: str) -> str:
        """
        Parses stock information to numeric format
        
        Returns:
            - Numeric string for exact quantities: '0', '1', '5', '8', etc.
            - '+10' for "Mayor a 10" (more than 10) - formato estándar
            - '0' for out of stock
        """
        if not stock_text:
            return '0'
        
        stock_text_lower = stock_text.lower()
        
        # Check for explicit number in text FIRST
        numbers = re.findall(r'\d+', stock_text)
        if numbers:
            qty = int(numbers[0])
            
            # Check if it says "Mayor a X" or similar
            if any(word in stock_text_lower for word in ['mayor a', 'más de', 'more than', 'mayor de']):
                # If "Mayor a 10" return "+10" (formato estándar)
                return f'+{qty}'
            
            # Regular number
            return str(qty)
        
        # Check for out of stock
        if any(word in stock_text_lower for word in ['agotado', 'sin stock', 'out of stock', 'no disponible']):
            return '0'
        
        # Check for available but no specific number
        if any(word in stock_text_lower for word in ['disponible', 'stock', 'en stock', 'available']):
            return '+5'
        
        if any(word in stock_text_lower for word in ['pocas unidades', 'últimas unidades', 'low stock']):
            return '1-4'
        
        return '0'
    
    def extract_brand_from_name(self, name: str) -> str:
        """Extracts brand from product name"""
        common_brands = [
            'Intel', 'AMD', 'NVIDIA', 'ASUS', 'MSI', 'Gigabyte', 'ASRock',
            'Corsair', 'Kingston', 'Samsung', 'Western Digital', 'WD',
            'Seagate', 'Crucial', 'G.Skill', 'HyperX', 'Razer',
            'Logitech', 'Cooler Master', 'NZXT', 'Thermaltake',
            'EVGA', 'Zotac', 'Sapphire', 'XFX', 'PNY', 'Palit',
            'Adata', 'Patriot', 'Team', 'Lexar'
        ]
        
        name_upper = name.upper()
        for brand in common_brands:
            if brand.upper() in name_upper:
                return brand
        
        # If no match, return first word
        return name.split()[0] if name else 'Unknown'
    
    def identify_component_type(self, name: str, category: str = '') -> str:
        """
        Identifies the type of PC component from name and category
        
        Args:
            name: Product name
            category: Category from website (if available)
            
        Returns:
            Component type string
        """
        text = (name + ' ' + category).lower()
        
        type_keywords = {
            'procesador': ['procesador', 'processor', 'cpu', 'core i', 'ryzen', 'pentium', 'celeron', 'athlon'],
            'tarjeta_grafica': ['tarjeta grafica', 'tarjeta gráfica', 'gpu', 'geforce', 'radeon', 'rtx', 'gtx', 'video card'],
            'memoria_ram': ['memoria', 'ram', 'ddr', 'dimm', 'memory'],
            'almacenamiento': ['ssd', 'hdd', 'nvme', 'disco', 'storage', 'm.2', 'sata'],
            'placa_madre': ['motherboard', 'placa madre', 'mainboard', 'board'],
            'fuente': ['fuente', 'psu', 'power supply'],
            'gabinete': ['gabinete', 'case', 'caja', 'chasis'],
            'refrigeracion': ['cooler', 'refrigeracion', 'refrigeración', 'ventilador', 'fan', 'liquid cooling'],
            'monitor': ['monitor', 'display', 'pantalla', 'screen'],
            'teclado': ['teclado', 'keyboard'],
            'mouse': ['mouse', 'ratón', 'raton'],
            'auriculares': ['auricular', 'headset', 'headphone']
        }
        
        for component_type, keywords in type_keywords.items():
            if any(keyword in text for keyword in keywords):
                return component_type
        
        return 'otro'
    
    def normalize_product_name(self, name: str) -> str:
        """
        Normalizes product name for better comparison between stores
        Removes common variations and standardizes format
        """
        # Convert to uppercase
        name = name.upper()
        
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Remove common words that don't affect product identity
        remove_words = [
            'PROCESADOR', 'PROCESSOR', 'CPU',
            'TARJETA GRAFICA', 'TARJETA GRÁFICA', 'GPU',
            'MEMORIA', 'RAM',
            'BOX', 'CAJA',
            '- NEGRO', '- BLANCO', '- BLACK', '- WHITE'
        ]
        
        for word in remove_words:
            name = name.replace(word, '')
        
        # Standardize brand names
        brand_variations = {
            'INTEL®': 'INTEL',
            'AMD®': 'AMD',
            'NVIDIA®': 'NVIDIA',
        }
        
        for old, new in brand_variations.items():
            name = name.replace(old, new)
        
        # Remove special characters except common ones
        name = re.sub(r'[^\w\s\-/.]', '', name)
        
        # Remove extra whitespace again
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def create_product_dict(self, **kwargs) -> Dict:
        """
        Creates a standardized product dictionary
        
        All store scrapers should use this to ensure consistent format
        """
        product = {
            'name': kwargs.get('name', ''),
            'normalized_name': self.normalize_product_name(kwargs.get('name', '')),
            'component_type': kwargs.get('component_type', ''),
            'brand': kwargs.get('brand', ''),
            'sku': kwargs.get('sku', ''),
            'price_usd': kwargs.get('price_usd', 0.0),
            'price_local': kwargs.get('price_local', 0.0),
            'currency': kwargs.get('currency', 'USD'),
            'stock': kwargs.get('stock', 'unknown'),
            'store': self.store_name,
            'source_url': kwargs.get('source_url', ''),
            'image_url': kwargs.get('image_url', ''),
            'last_scraped': datetime.now().isoformat(),
            'metadata': kwargs.get('metadata', {})
        }
        
        # Auto-detect component type if not provided
        if not product['component_type']:
            product['component_type'] = self.identify_component_type(
                product['name'], 
                kwargs.get('category', '')
            )
        
        # Auto-detect brand if not provided
        if not product['brand']:
            product['brand'] = self.extract_brand_from_name(product['name'])
        
        return product
    
    def scrape_with_retry(self, url: str, max_retries: int = 3, delay: int = 2) -> Optional[BeautifulSoup]:
        """
        Fetches a page with retry logic
        
        Args:
            url: URL to fetch
            max_retries: Maximum number of retry attempts
            delay: Delay between retries in seconds
            
        Returns:
            BeautifulSoup object or None
        """
        for attempt in range(max_retries):
            soup = self.fetch_page(url)
            if soup:
                return soup
            
            if attempt < max_retries - 1:
                print(f"⚠️ Retry {attempt + 1}/{max_retries} for {url}")
                time.sleep(delay)
        
        return None
