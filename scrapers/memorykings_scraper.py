"""
MemoryKings Store Scraper
Specialized scraper for memorykings.pe
"""

import re
from typing import List, Dict, Optional
from .base_scraper import BaseScraper


class MemoryKingsScraper(BaseScraper):
    """Scraper específico para MemoryKings"""
    
    def __init__(self, use_selenium: bool = True):
        super().__init__('MemoryKings', use_selenium=use_selenium)
        self.base_url = 'https://www.memorykings.pe'
    
    def scrape_product_page(self, url: str) -> Optional[Dict]:
        """
        Scrapes a single product page from MemoryKings
        
        Estructura HTML de MemoryKings:
        - Título: h1 en página de producto
        - Precio: $345.00 ó S/ 1,186.50 format
        - Número de Parte: div con "Número de Parte:"
        - Código Interno: div con "Código Interno:"
        - Stock: div con "Stock:"
        """
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        try:
            product_data = {}
            
            # Extract product name - usually in h1
            name_elem = soup.find('h1')
            if not name_elem:
                name_elem = soup.find('div', class_=re.compile('product-title|titulo'))
            
            if not name_elem:
                print(f"❌ No se encontró nombre en {url}")
                return None
            
            product_data['name'] = name_elem.get_text(strip=True)
            
            # Extract price - format: $ 345.00 ó S/ 1,186.50
            price_container = soup.find('div', class_=re.compile('price|precio'))
            if not price_container:
                # Try to find by text pattern
                price_text = soup.find(text=re.compile(r'\$\s*[\d,\.]+'))
                if price_text:
                    if hasattr(price_text, 'parent'):
                        price_container = price_text.parent
            
            if price_container:
                price_text = price_container.get_text(strip=True)
                prices = self.parse_price(price_text)
                product_data.update(prices)
            
            # Extract Número de Parte (Part Number)
            part_number_elem = soup.find(text=re.compile('Número de Parte'))
            if part_number_elem:
                # Get the parent and try to find the value
                parent = part_number_elem.parent
                if parent:
                    # Look for strong or next sibling with the value
                    value_elem = parent.find_next('strong')
                    if value_elem:
                        product_data['sku'] = value_elem.get_text(strip=True)
                    else:
                        # Try to extract from text
                        full_text = parent.get_text(strip=True)
                        match = re.search(r'Número de Parte:\s*(\w+)', full_text)
                        if match:
                            product_data['sku'] = match.group(1)
            
            # Extract Código Interno (Internal Code)
            codigo_elem = soup.find(text=re.compile('Código Interno'))
            if codigo_elem:
                parent = codigo_elem.parent
                if parent:
                    value_elem = parent.find_next('strong')
                    if value_elem:
                        codigo = value_elem.get_text(strip=True)
                        if not product_data.get('sku'):
                            product_data['sku'] = codigo
                        product_data['internal_code'] = codigo
            
            # Extract stock
            stock_elem = soup.find(text=re.compile('Stock'))
            if stock_elem:
                parent = stock_elem.parent
                if parent:
                    stock_text = parent.get_text(strip=True)
                    product_data['stock'] = self.parse_stock(stock_text)
            
            # Extract brand - usually in the title or specific div
            brand_elem = soup.find('div', class_=re.compile('brand|marca'))
            if brand_elem:
                product_data['brand'] = brand_elem.get_text(strip=True)
            
            # Create product dict
            if 'price_usd' not in product_data:
                print(f"⚠️ No se encontró precio en {url}")
                return None
            
            product = self.create_product_dict(
                name=product_data['name'],
                brand=product_data.get('brand', ''),
                sku=product_data.get('sku', ''),
                price_usd=product_data.get('price_usd', 0.0),
                price_local=product_data.get('price_local', 0.0),
                currency=product_data.get('currency', 'USD'),
                stock=product_data.get('stock', 'unknown'),
                source_url=url,
                metadata={
                    'internal_code': product_data.get('internal_code', ''),
                }
            )
            
            return product
            
        except Exception as e:
            print(f"❌ Error extrayendo producto de MemoryKings: {e}")
            return None
    
    def scrape_category_page(self, url: str) -> List[Dict]:
        """
        Scrapes a category/listing page from MemoryKings
        
        Encuentra los enlaces a productos y los scrapea individualmente
        """
        soup = self.fetch_page(url)
        if not soup:
            return []
        
        products = []
        
        # Find product links - MemoryKings uses /producto/ in URLs
        product_links = soup.find_all('a', href=re.compile(r'/producto/|/productos/'))
        
        # Remove duplicates
        unique_urls = set()
        for link in product_links:
            href = link.get('href')
            if href:
                if not href.startswith('http'):
                    href = self.base_url + href
                unique_urls.add(href)
        
        print(f"📦 Encontrados {len(unique_urls)} productos únicos en la página")
        
        for product_url in unique_urls:
            try:
                print(f"  → Scraping: {product_url}")
                product = self.scrape_product_page(product_url)
                
                if product:
                    products.append(product)
                    
            except Exception as e:
                print(f"⚠️ Error procesando {product_url}: {e}")
                continue
        
        return products
    
    def scrape_category_quick(self, url: str) -> List[Dict]:
        """
        Quick scrape from category page without visiting individual pages
        Extrae información básica del listado
        """
        soup = self.fetch_page(url)
        if not soup:
            return []
        
        products = []
        
        # Find product containers
        product_containers = soup.find_all('div', class_=re.compile('product-item|producto-item|card-product'))
        
        for container in product_containers:
            try:
                product_data = {}
                
                # Name
                name_elem = container.find(['h2', 'h3', 'h4', 'a'], class_=re.compile('title|nombre|name'))
                if not name_elem:
                    name_elem = container.find('a')
                
                if name_elem:
                    product_data['name'] = name_elem.get_text(strip=True)
                else:
                    continue
                
                # Price
                price_elem = container.find(class_=re.compile('price|precio'))
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    prices = self.parse_price(price_text)
                    product_data.update(prices)
                
                # URL
                link = container.find('a', href=re.compile(r'/producto/'))
                if link:
                    product_url = link['href']
                    if not product_url.startswith('http'):
                        product_url = self.base_url + product_url
                    product_data['source_url'] = product_url
                
                if 'price_usd' in product_data:
                    product = self.create_product_dict(**product_data)
                    products.append(product)
                    
            except Exception as e:
                continue
        
        return products
