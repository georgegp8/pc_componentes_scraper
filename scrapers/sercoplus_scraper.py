"""
SercoPlus Store Scraper
Specialized scraper for sercoplus.com
"""

import re
from typing import List, Dict, Optional
from .base_scraper import BaseScraper


class SercoPlusScraper(BaseScraper):
    """Scraper específico para SercoPlus"""
    
    def __init__(self, use_selenium: bool = True):
        super().__init__('SercoPlus', use_selenium=use_selenium)
        self.base_url = 'https://sercoplus.com'
    
    def scrape_product_page(self, url: str) -> Optional[Dict]:
        """
        Scrapes a single product page from SercoPlus
        
        Estructura HTML de SercoPlus:
        - Nombre: h1.h1[itemprop="name"]
        - Precio efectivo: div.product-price span.price (primer precio)
        - Precio con tarjeta: div.product-price-charged span.price
        - SKU: span[itemprop="sku"]
        - Marca: meta[itemprop="brand"]
        - Stock: div.tv-items span.tvinstock
        - Número de Parte: Buscar en div.product-summary
        """
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        try:
            product_data = {}
            
            # Extract product name
            name_elem = soup.find('h1', class_='h1', itemprop='name')
            if not name_elem:
                print(f"❌ No se encontró nombre en {url}")
                return None
            
            product_data['name'] = name_elem.get_text(strip=True)
            
            # Extract prices (efectivo)
            price_container = soup.find('div', class_='product-price')
            if price_container:
                price_span = price_container.find('span', class_='price', itemprop='price')
                if price_span:
                    price_text = price_span.get_text(strip=True)
                    prices = self.parse_price(price_text)
                    product_data.update(prices)
            
            # If no price found in first container, try charged price
            if 'price_usd' not in product_data:
                charged_container = soup.find('div', class_='product-price-charged')
                if charged_container:
                    price_span = charged_container.find('span', class_='price')
                    if price_span:
                        price_text = price_span.get_text(strip=True)
                        prices = self.parse_price(price_text)
                        product_data.update(prices)
            
            # Extract SKU
            sku_elem = soup.find('span', itemprop='sku')
            if sku_elem:
                product_data['sku'] = sku_elem.get_text(strip=True)
            
            # Extract Part Number (Número de Parte)
            summary_div = soup.find('div', id=re.compile('product-description-short'))
            if summary_div:
                part_number_text = summary_div.find('h4')
                if part_number_text:
                    pn_text = part_number_text.get_text(strip=True)
                    # Extract: "Número de Parte: BX8071512400F"
                    pn_match = re.search(r'Número de Parte:\s*(\w+)', pn_text)
                    if pn_match:
                        product_data['part_number'] = pn_match.group(1)
            
            # Extract brand
            brand_elem = soup.find('meta', attrs={'itemprop': 'brand'})
            if brand_elem:
                brand_content = brand_elem.get('content')
                if brand_content:
                    product_data['brand'] = brand_content
            else:
                # Try to find in product-manufacturer
                brand_div = soup.find('div', class_='product-manufacturer')
                if brand_div:
                    brand_link = brand_div.find('a')
                    if brand_link:
                        product_data['brand'] = brand_link.get_text(strip=True)
            
            # Extract stock
            stock_elem = soup.find('span', class_='tvinstock')
            if stock_elem:
                stock_text = stock_elem.get_text(strip=True)
                product_data['stock'] = self.parse_stock(stock_text)
            else:
                # Try alternative stock location
                stock_container = soup.find('div', class_='tv-items')
                if stock_container:
                    stock_text = stock_container.get_text(strip=True)
                    product_data['stock'] = self.parse_stock(stock_text)
            
            # Extract category/component type
            breadcrumb = soup.find('nav', attrs={'aria-label': 'breadcrumb'}) or soup.find('ol', class_='breadcrumb')
            category = ''
            if breadcrumb:
                links = breadcrumb.find_all('a')
                if len(links) >= 2:
                    category = links[-1].get_text(strip=True)
            
            # Create product dict with all info
            if 'price_usd' not in product_data:
                print(f"⚠️ No se encontró precio en {url}")
                return None
            
            product = self.create_product_dict(
                name=product_data['name'],
                brand=product_data.get('brand', ''),
                sku=product_data.get('sku', product_data.get('part_number', '')),
                price_usd=product_data.get('price_usd', 0.0),
                price_local=product_data.get('price_local', 0.0),
                currency=product_data.get('currency', 'USD'),
                stock=product_data.get('stock', 'unknown'),
                source_url=url,
                category=category,
                metadata={
                    'part_number': product_data.get('part_number', ''),
                    'category': category
                }
            )
            
            return product
            
        except Exception as e:
            print(f"❌ Error extrayendo producto de SercoPlus: {e}")
            return None
    
    def scrape_category_page(self, url: str, max_pages: int = None) -> List[Dict]:
        """
        Scrapes a category/listing page from SercoPlus with pagination support
        
        Args:
            url: Category URL
            max_pages: Maximum number of pages to scrape (None = all pages)
        
        Estructura HTML (actualizada Nov 2025):
        - Contenedores de productos: article.product-miniature
        - Nombre: div.tvproduct-name.product-title > a > h6
        - Precio: span.price
        - URL: div.tvproduct-name.product-title > a[href]
        - Stock: div.tvproduct-stock > span.value
        - Referencia: div.tvproduct-reference > span.value
        - Paginación: a.js-search-link con data-query-param="?page=X"
        """
        all_products = []
        current_page = 1
        
        while True:
            # Build page URL
            if current_page == 1:
                page_url = url
            else:
                # Add page parameter
                separator = '&' if '?' in url else '?'
                page_url = f"{url}{separator}page={current_page}"
            
            print(f"   📄 Página {current_page}: {page_url}")
            
            soup = self.fetch_page(page_url, wait_time=5)
            if not soup:
                break
            
            # Find all product containers (article.product-miniature)
            product_containers = soup.find_all('article', class_='product-miniature')
            
            if not product_containers:
                print("      ⚠️ No se encontraron productos en esta página")
                break
            
            print(f"      📦 Encontrados {len(product_containers)} productos")
            
            page_products = 0
            for container in product_containers:
                try:
                    product_data = {}
                    
                    # Extract product name
                    name_elem = container.find('div', class_='product-title')
                    if name_elem:
                        name_link = name_elem.find('a')
                        if name_link:
                            h6 = name_link.find('h6')
                            if h6:
                                product_data['name'] = h6.get_text(strip=True)
                                product_data['source_url'] = name_link.get('href', '')
                    
                    if not product_data.get('name'):
                        continue  # Skip if no name
                    
                    # Extract price
                    price_elem = container.find('span', class_='price')
                    if price_elem:
                        price_text = price_elem.get_text(strip=True)
                        prices = self.parse_price(price_text)
                        product_data.update(prices)
                    
                    # Extract reference/SKU
                    ref_div = container.find('div', class_='tvproduct-reference')
                    if ref_div:
                        ref_span = ref_div.find('span', class_='value')
                        if ref_span:
                            product_data['sku'] = ref_span.get_text(strip=True)
                    
                    # Extract stock
                    stock_div = container.find('div', class_='tvproduct-stock')
                    if stock_div:
                        stock_span = stock_div.find('span', class_='value')
                        if stock_span:
                            stock_text = stock_span.get_text(strip=True)
                            product_data['stock'] = self.parse_stock(stock_text)
                    
                    # Extract image URL
                    img_elem = container.find('img', class_='tvproduct-hover-img')
                    if img_elem and img_elem.get('src'):
                        product_data['image_url'] = img_elem['src']
                    
                    # Create product dict
                    if 'price_usd' in product_data:
                        product = self.create_product_dict(
                            name=product_data['name'],
                            brand=product_data.get('brand', ''),
                            sku=product_data.get('sku', ''),
                            price_usd=product_data.get('price_usd', 0.0),
                            price_local=product_data.get('price_local', 0.0),
                            currency=product_data.get('currency', 'USD'),
                            stock=product_data.get('stock', 'unknown'),
                            source_url=product_data.get('source_url', page_url),
                            category='',
                            image_url=product_data.get('image_url', ''),
                            metadata={}
                        )
                        all_products.append(product)
                        page_products += 1
                            
                except Exception as e:
                    print(f"      ⚠️ Error procesando contenedor: {e}")
                    continue
            
            print(f"      ✅ {page_products} productos agregados")
            
            # Check if there's a next page
            next_page = soup.find('a', class_='js-search-link', attrs={'rel': 'next'})
            if not next_page:
                # Alternative: look for pagination links
                pagination = soup.find('nav', class_='pagination')
                if pagination:
                    next_link = pagination.find('a', class_='next')
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
    
    def scrape_category_quick(self, url: str) -> List[Dict]:
        """
        Quick scrape from category page without visiting individual product pages
        Faster but less complete data
        """
        soup = self.fetch_page(url)
        if not soup:
            return []
        
        products = []
        product_containers = soup.find_all('div', class_=re.compile('product-miniature|tv-product'))
        
        for container in product_containers:
            try:
                product_data = {}
                
                # Name
                name_elem = container.find(['h2', 'h3', 'a'], class_=re.compile('product-title|product-name'))
                if name_elem:
                    product_data['name'] = name_elem.get_text(strip=True)
                else:
                    continue
                
                # Price
                price_elem = container.find('span', class_='price')
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    prices = self.parse_price(price_text)
                    product_data.update(prices)
                
                # URL
                link = container.find('a', href=re.compile(r'/\d+-'))
                if link:
                    product_url = link['href']
                    if not product_url.startswith('http'):
                        product_url = self.base_url + product_url
                    product_data['source_url'] = product_url
                
                # SKU (if available in listing)
                ref_elem = container.find(text=re.compile('Ref'))
                if ref_elem:
                    ref_text = ref_elem.parent.get_text(strip=True)
                    sku_match = re.search(r':\s*(\w+)', ref_text)
                    if sku_match:
                        product_data['sku'] = sku_match.group(1)
                
                if 'price_usd' in product_data:
                    product = self.create_product_dict(**product_data)
                    products.append(product)
                    
            except Exception as e:
                continue
        
        return products
