"""
CycComputer Store Scraper
Specialized scraper for cyccomputer.pe
"""

import re
import sys
import os
from typing import List, Dict, Optional
from urllib.parse import urlencode, urlparse, parse_qs

# Add parent directory to path to import base_scraper
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from base_scraper import BaseScraper


class CycComputerScraper(BaseScraper):
    """Scraper específico para CycComputer"""
    
    def __init__(self, use_selenium: bool = True):
        super().__init__('CycComputer', use_selenium=use_selenium)
        self.base_url = 'https://cyccomputer.pe'
    
    def scrape_product_page(self, url: str) -> Optional[Dict]:
        """
        Scrapes a single product page from CycComputer
        (No usado actualmente - scraping desde listings)
        """
        return None
    
    def scrape_category_page(self, url: str, max_pages: int = None) -> List[Dict]:
        """
        Scrapes a category/listing page from CycComputer with pagination support
        
        Args:
            url: Category URL (ej: https://cyccomputer.pe/categoria/233-placas-madre)
            max_pages: Maximum number of pages to scrape (None = all pages)
        """
        all_products = []
        seen_urls = set()  # Para evitar duplicados
        current_page = 1
        
        while True:
            # Build page URL
            if current_page == 1:
                page_url = url
            else:
                # CycComputer usa ?page=N para paginación
                separator = '&' if '?' in url else '?'
                page_url = f"{url}{separator}page={current_page}"
            
            print(f"   📄 Página {current_page}: {page_url}")
            
            soup = self.fetch_page(page_url, wait_time=5)
            if not soup:
                break
            
            # Find all product containers - CycComputer usa div.item-inner
            product_containers = soup.find_all('div', class_='item-inner')
            
            if not product_containers:
                print("      ⚠️ No se encontraron productos en esta página")
                break
            
            print(f"      📦 Encontrados {len(product_containers)} productos")
            
            page_products = 0
            for container in product_containers:
                try:
                    product_data = {}
                    
                    # Extract product name - h2.productName > a
                    name_elem = container.find('h2', class_='productName')
                    if name_elem:
                        link = name_elem.find('a')
                        if link:
                            product_data['name'] = link.get_text(strip=True)
                            href = link.get('href', '')
                            if href and not href.startswith('http'):
                                href = self.base_url + href
                            product_data['source_url'] = href
                    
                    if not product_data.get('name'):
                        continue  # Skip if no name
                    
                    # Skip si ya vimos esta URL (evitar duplicados)
                    if product_data.get('source_url') in seen_urls:
                        continue
                    
                    # Extract price - span.price con formato "$\u00a0<precio> (S/\u00a0<precio_local>)"
                    price_elem = container.find('span', class_='price')
                    if price_elem:
                        price_text = price_elem.get_text(strip=True)
                        prices = self.parse_price(price_text)
                        product_data.update(prices)
                    
                    # Extract stock - div.quantity con formato "Mayor a 10 Artículos" o similar
                    stock_elem = container.find('div', class_='quantity')
                    if stock_elem:
                        stock_text = stock_elem.get_text(strip=True)
                        # Extraer el número o texto después de "Stock:"
                        stock_match = re.search(r'Stock:\s*(.+)', stock_text, re.IGNORECASE)
                        if stock_match:
                            stock_value = stock_match.group(1).strip()
                            
                            # Convertir "Mayor a X Artículos" a "+X" (formato estándar: +10)
                            mayor_match = re.search(r'Mayor\s+a\s+(\d+)', stock_value, re.IGNORECASE)
                            if mayor_match:
                                product_data['stock'] = f"+{mayor_match.group(1)}"
                            # Convertir "X Artículos" a "X"
                            elif re.search(r'(\d+)\s+Artículo', stock_value, re.IGNORECASE):
                                num_match = re.search(r'(\d+)', stock_value)
                                if num_match:
                                    product_data['stock'] = num_match.group(1)
                            else:
                                product_data['stock'] = self.parse_stock(stock_value)
                        else:
                            product_data['stock'] = 'unknown'
                    
                    # Extract brand - div.manufacturer_name
                    brand_elem = container.find('div', class_='manufacturer_name')
                    if brand_elem:
                        brand_text = brand_elem.get_text(strip=True)
                        # Extraer después de "Marca:"
                        brand_match = re.search(r'Marca:\s*(.+)', brand_text, re.IGNORECASE)
                        if brand_match:
                            product_data['brand'] = brand_match.group(1).strip()
                    
                    # Extract image URL - img en laberProduct-image
                    img_container = container.find('div', class_='laberProduct-image')
                    if img_container:
                        img_elem = img_container.find('img')
                        if img_elem:
                            img_src = img_elem.get('src') or img_elem.get('data-src')
                            if img_src:
                                if not img_src.startswith('http'):
                                    img_src = self.base_url + img_src
                                product_data['image_url'] = img_src
                    
                    # Extract SKU from URL if available (formato: /10652640-nombre-producto.html)
                    if product_data.get('source_url'):
                        sku_match = re.search(r'/(\d+)-', product_data['source_url'])
                        if sku_match:
                            product_data['sku'] = sku_match.group(1)
                    
                    # Create product dict
                    if 'price_usd' in product_data or 'price_local' in product_data:
                        product = self.create_product_dict(
                            name=product_data['name'],
                            brand=product_data.get('brand', ''),
                            sku=product_data.get('sku', ''),
                            price_usd=product_data.get('price_usd', 0.0),
                            price_local=product_data.get('price_local', 0.0),
                            currency=product_data.get('currency', 'PEN'),
                            stock=product_data.get('stock', 'unknown'),
                            source_url=product_data.get('source_url', page_url),
                            category='',
                            image_url=product_data.get('image_url', ''),
                            metadata={},
                            component_type=''  # Se asignará luego en run.py
                        )
                        all_products.append(product)
                        seen_urls.add(product_data.get('source_url'))  # Marcar como visto
                        page_products += 1
                            
                except Exception as e:
                    print(f"      ⚠️ Error procesando contenedor: {e}")
                    continue
            
            print(f"      ✅ {page_products} productos agregados")
            
            # Check if there's a next page
            # Buscar botón "siguiente" o paginación
            next_page = soup.find('a', class_=re.compile('next|siguiente'))
            if not next_page:
                # Buscar en paginación numerada
                pagination = soup.find(['nav', 'div', 'ul'], class_=re.compile('paginat'))
                if pagination:
                    # Buscar si existe el número de la siguiente página
                    next_link = pagination.find('a', text=str(current_page + 1))
                    if not next_link:
                        break
                else:
                    break
            
            current_page += 1
            
            # Check max_pages limit
            if max_pages and current_page > max_pages:
                print(f"      ⚠️ Límite de {max_pages} páginas alcanzado")
                break
            
            # Delay between pages
            import time
            time.sleep(2)
        
        print(f"   📊 Total: {len(all_products)} productos de {current_page} página(s)")
        return all_products
