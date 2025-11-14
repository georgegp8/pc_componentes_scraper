"""
Impacto Store Scraper
Specialized scraper for impacto.com.pe
"""

import re
import sys
import os
from typing import List, Dict, Optional
from urllib.parse import urlencode, urlparse, parse_qs

# Add parent directory to path to import base_scraper
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from base_scraper import BaseScraper


class ImpactoScraper(BaseScraper):
    """Scraper específico para Impacto"""
    
    def __init__(self, use_selenium: bool = True):
        super().__init__('Impacto', use_selenium=use_selenium)
        self.base_url = 'https://www.impacto.com.pe'
    
    def scrape_product_page(self, url: str) -> Optional[Dict]:
        """
        Scrapes a single product page from Impacto
        
        La estructura HTML de Impacto será similar a otras tiendas peruanas
        """
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        try:
            product_data = {}
            
            # Extract product name (ajustar según HTML real)
            name_elem = soup.find('h1', class_=re.compile('product|title|nombre'))
            if not name_elem:
                # Intentar otros selectores comunes
                name_elem = soup.find('h1')
            
            if not name_elem:
                print(f"❌ No se encontró nombre en {url}")
                return None
            
            product_data['name'] = name_elem.get_text(strip=True)
            
            # Extract price (ajustar según HTML real)
            price_container = soup.find(['div', 'span'], class_=re.compile('price|precio'))
            if price_container:
                price_text = price_container.get_text(strip=True)
                prices = self.parse_price(price_text)
                product_data.update(prices)
            
            # If no price found, try meta tags
            if 'price_usd' not in product_data:
                price_meta = soup.find('meta', property='product:price:amount')
                if price_meta and price_meta.get('content'):
                    try:
                        price = float(price_meta['content'])
                        product_data['price_usd'] = price
                        product_data['currency'] = 'PEN'
                    except:
                        pass
            
            # Extract SKU
            sku_elem = soup.find(['span', 'div'], class_=re.compile('sku|codigo|code'))
            if sku_elem:
                sku_text = sku_elem.get_text(strip=True)
                sku_match = re.search(r'SKU[:\s]*(\w+)', sku_text, re.IGNORECASE)
                if sku_match:
                    product_data['sku'] = sku_match.group(1)
                else:
                    product_data['sku'] = sku_text
            
            # Extract brand
            brand_elem = soup.find(['span', 'div', 'a'], class_=re.compile('brand|marca'))
            if brand_elem:
                product_data['brand'] = brand_elem.get_text(strip=True)
            
            # Extract stock
            stock_elem = soup.find(['span', 'div'], class_=re.compile('stock|disponib'))
            if stock_elem:
                stock_text = stock_elem.get_text(strip=True)
                product_data['stock'] = self.parse_stock(stock_text)
            
            # Extract image
            img_elem = soup.find('img', class_=re.compile('product|main'))
            if img_elem and img_elem.get('src'):
                product_data['image_url'] = img_elem['src']
            
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
                currency=product_data.get('currency', 'PEN'),
                stock=product_data.get('stock', 'unknown'),
                source_url=url,
                image_url=product_data.get('image_url', ''),
                category='',
                metadata={}
            )
            
            return product
            
        except Exception as e:
            print(f"❌ Error extrayendo producto de Impacto: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def scrape_category_page(self, url: str, max_pages: int = None) -> List[Dict]:
        """
        Scrapes a category/listing page from Impacto with pagination support
        
        Args:
            url: Category URL (ej: https://www.impacto.com.pe/catalogo?categoria=Procesador&c=19)
            max_pages: Maximum number of pages to scrape (None = all pages)
        
        La estructura parece usar parámetros de query para paginación
        """
        all_products = []
        current_page = 1
        
        # Parse URL to get base and params
        parsed_url = urlparse(url)
        base_params = parse_qs(parsed_url.query)
        
        while True:
            # Build page URL
            if current_page == 1:
                page_url = url
            else:
                # Add page parameter (ajustar según la paginación real de Impacto)
                params = base_params.copy()
                params['page'] = [str(current_page)]  # o 'p', 'pagina', etc.
                page_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{urlencode(params, doseq=True)}"
            
            print(f"   📄 Página {current_page}: {page_url}")
            
            soup = self.fetch_page(page_url, wait_time=5)
            if not soup:
                break
            
            # Find all product containers - Impacto usa div.single-product
            product_containers = soup.find_all('div', class_='single-product')
            
            if not product_containers:
                # Fallback a selector genérico
                product_containers = soup.find_all('a', href=re.compile(r'/producto/'))
            
            if not product_containers:
                print("      ⚠️ No se encontraron productos en esta página")
                break
            
            print(f"      📦 Encontrados {len(product_containers)} productos")
            
            page_products = 0
            for container in product_containers:
                try:
                    product_data = {}
                    
                    # Extract product name - Impacto usa h4.product-title > a
                    name_elem = container.find('h4', class_='product-title')
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
                    
                    # Extract price - Impacto usa span.price-sale-2 con formato "$28.50 - S/96.90"
                    price_elem = container.find('span', class_='price-sale-2')
                    if price_elem:
                        price_text = price_elem.get_text(strip=True)
                        prices = self.parse_price(price_text)
                        product_data.update(prices)
                    
                    # Extract MINICÓDIGO (SKU) y STOCK - dentro de div.detail
                    detail_div = container.find('div', class_='detail')
                    if detail_div:
                        detail_text = detail_div.get_text()
                        
                        # Buscar MINICÓDIGO: 021515
                        sku_match = re.search(r'MINICÓDIGO:\s*(\d+)', detail_text)
                        if sku_match:
                            product_data['sku'] = sku_match.group(1)
                        
                        # Extract STOCK - formato "STOCK: +10" o "STOCK: 5"
                        stock_match = re.search(r'STOCK:\s*([+\d]+)', detail_text)
                        if stock_match:
                            stock_text = stock_match.group(1)
                            product_data['stock'] = self.parse_stock(stock_text)
                    
                    # Extract image URL - primera imagen en div.product-image
                    img_elem = container.find('img', class_='first-image')
                    if img_elem:
                        img_src = img_elem.get('src') or img_elem.get('data-src')
                        if img_src:
                            if not img_src.startswith('http'):
                                img_src = self.base_url + img_src
                            product_data['image_url'] = img_src
                    
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

