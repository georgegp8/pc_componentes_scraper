"""
PCImpacto Store Scraper
Specialized scraper for impacto.com.pe
"""

import re
from typing import List, Dict, Optional
from .base_scraper import BaseScraper


class PCImpactoScraper(BaseScraper):
    """Scraper específico para PCImpacto"""
    
    def __init__(self, use_selenium: bool = True):
        super().__init__('PCImpacto', use_selenium=use_selenium)
        self.base_url = 'https://www.impacto.com.pe'
    
    def scrape_product_page(self, url: str) -> Optional[Dict]:
        """
        Scrapes a single product page from PCImpacto
        
        Estructura HTML de PCImpacto:
        - Título: h1.product-title
        - Mini código: span con "MINICÓDIGO:"
        - Part Number: span con "PN:"
        - Stock: span con "STOCK:"
        - Marca: a con href="/catalogo?marca="
        - Precio efectivo: span.regular-price (en general-prices-all)
        - Precio con tarjeta: span.regular-price-3
        """
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        try:
            product_data = {}
            
            # Extract product name
            name_elem = soup.find('h1', class_='product-title')
            if not name_elem:
                # Alternative: try to find h1 in single-product-content
                name_elem = soup.find('div', class_='single-product-content')
                if name_elem:
                    name_elem = name_elem.find('h1')
            
            if not name_elem:
                print(f"❌ No se encontró nombre en {url}")
                return None
            
            product_data['name'] = name_elem.get_text(strip=True)
            
            # Extract MINICÓDIGO (mini code)
            minicodigo_elem = soup.find('span', text=re.compile('MINICÓDIGO'))
            if minicodigo_elem:
                # Get next span or text
                parent = minicodigo_elem.find_parent('div')
                if parent:
                    full_text = parent.get_text(strip=True)
                    match = re.search(r'MINICÓDIGO:\s*(\d+)', full_text)
                    if match:
                        product_data['minicodigo'] = match.group(1)
            
            # Extract Part Number (PN)
            pn_elem = soup.find('span', text=re.compile('PN:'))
            if not pn_elem:
                pn_elem = soup.find(text=re.compile('PN:'))
            
            if pn_elem:
                parent = pn_elem.parent if hasattr(pn_elem, 'parent') else pn_elem
                full_text = parent.get_text(strip=True) if hasattr(parent, 'get_text') else str(parent)
                match = re.search(r'PN:\s*(\w+)', full_text)
                if match:
                    product_data['sku'] = match.group(1)
            
            # Extract Número de Parte (alternative location)
            if not product_data.get('sku'):
                part_elem = soup.find('h6', text=re.compile('Número de Parte'))
                if part_elem:
                    full_text = part_elem.get_text(strip=True)
                    match = re.search(r':\s*(\w+)', full_text)
                    if match:
                        product_data['sku'] = match.group(1)
            
            # Extract stock
            stock_elem = soup.find('span', text=re.compile('STOCK'))
            if not stock_elem:
                stock_elem = soup.find(text=re.compile('Stock'))
            
            if stock_elem:
                parent = stock_elem.parent if hasattr(stock_elem, 'parent') else stock_elem
                stock_text = parent.get_text(strip=True) if hasattr(parent, 'get_text') else str(parent)
                product_data['stock'] = self.parse_stock(stock_text)
            
            # Extract brand - usually a link with /catalogo?marca=
            brand_elem = soup.find('a', href=re.compile(r'/catalogo\?marca='))
            if brand_elem:
                product_data['brand'] = brand_elem.get_text(strip=True)
            else:
                # Alternative: look in card-body h6
                card_body = soup.find('div', class_='card-body')
                if card_body:
                    marca_h6 = card_body.find('h6', text=re.compile('Marca'))
                    if marca_h6:
                        brand_text = marca_h6.get_text(strip=True)
                        match = re.search(r':\s*(.+?)(?:\s|$)', brand_text)
                        if match:
                            product_data['brand'] = match.group(1).strip()
            
            # Extract prices - Look for "Pagando con Efectivo" section
            prices_container = soup.find('div', class_='general-prices-all')
            if not prices_container:
                prices_container = soup.find('div', class_=re.compile('product-price'))
            
            if prices_container:
                # Try to find "Pagando con Efectivo" price
                efectivo_section = None
                for div in prices_container.find_all('div', class_='product-price'):
                    text = div.get_text()
                    if 'Efectivo' in text or 'efectivo' in text:
                        efectivo_section = div
                        break
                
                if efectivo_section:
                    price_span = efectivo_section.find('span', class_=re.compile('regular-price'))
                    if price_span:
                        price_text = price_span.get_text(strip=True)
                        prices = self.parse_price(price_text)
                        product_data.update(prices)
                else:
                    # Fallback: get first price found
                    price_span = prices_container.find('span', class_=re.compile('price'))
                    if price_span:
                        price_text = price_span.get_text(strip=True)
                        prices = self.parse_price(price_text)
                        product_data.update(prices)
            
            # Extract category
            card_body = soup.find('div', class_='card-body')
            category = ''
            if card_body:
                generacion_elem = card_body.find('h6', text=re.compile('Generación'))
                if generacion_elem:
                    category = generacion_elem.get_text(strip=True)
            
            # Create product dict
            if 'price_usd' not in product_data:
                print(f"⚠️ No se encontró precio en {url}")
                return None
            
            product = self.create_product_dict(
                name=product_data['name'],
                brand=product_data.get('brand', ''),
                sku=product_data.get('sku', product_data.get('minicodigo', '')),
                price_usd=product_data.get('price_usd', 0.0),
                price_local=product_data.get('price_local', 0.0),
                currency=product_data.get('currency', 'USD'),
                stock=product_data.get('stock', 'unknown'),
                source_url=url,
                category=category,
                metadata={
                    'minicodigo': product_data.get('minicodigo', ''),
                    'part_number': product_data.get('sku', ''),
                    'category': category
                }
            )
            
            return product
            
        except Exception as e:
            print(f"❌ Error extrayendo producto de PCImpacto: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def scrape_category_page(self, url: str) -> List[Dict]:
        """
        Scrapes a category/listing page from PCImpacto
        
        Encuentra los enlaces a productos y los scrapea individualmente
        """
        soup = self.fetch_page(url)
        if not soup:
            return []
        
        products = []
        
        # Find product links - PCImpacto uses /producto/ in URLs
        product_links = soup.find_all('a', href=re.compile(r'/producto/'))
        
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
        
        # Find product containers in listings
        product_containers = soup.find_all('div', class_=re.compile('product-card|product-item|col-lg'))
        
        for container in product_containers:
            try:
                product_data = {}
                
                # Name
                name_elem = container.find(['h2', 'h3', 'h4'], class_=re.compile('title|name'))
                if not name_elem:
                    name_elem = container.find('a', href=re.compile(r'/producto/'))
                
                if name_elem:
                    product_data['name'] = name_elem.get_text(strip=True)
                else:
                    continue
                
                # Price
                price_elem = container.find('span', class_=re.compile('price'))
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
