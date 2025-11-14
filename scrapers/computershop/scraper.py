"""
ComputerShop Peru Scraper
Scraper específico para computershopperu.com
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_scraper import BaseScraper
from typing import List, Dict, Optional
import re
import time


class ComputerShopScraper(BaseScraper):
    """Scraper para ComputerShop Peru (computershopperu.com)"""
    
    def __init__(self, use_selenium: bool = True):
        super().__init__(store_name='computershop', use_selenium=use_selenium)
        self.base_url = 'https://computershopperu.com'
    
    def scrape_product_page(self, url: str) -> Optional[Dict]:
        """
        Scrapes a single product page from ComputerShop
        
        Args:
            url: Product page URL
            
        Returns:
            Product dictionary or None
        """
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        try:
            product_container = soup.find('div', class_='product-container')
            if not product_container:
                return None
            
            # Extract product name
            name_elem = product_container.find('h5', class_='product-name')
            if not name_elem or not name_elem.find('a'):
                return None
            name = name_elem.find('a').get_text(strip=True)
            
            # Extract image URL
            img_elem = product_container.find('img', class_='img-fluid')
            image_url = img_elem.get('src', '') if img_elem else ''
            
            # Extract price (formato: "$&nbsp;26,00&nbsp;&nbsp;&nbsp;(S/&nbsp;89,70)")
            price_elem = product_container.find('span', class_='product-price')
            price_data = self._extract_price(price_elem)
            
            # Extract stock
            stock_elem = product_container.find('span', class_='stock-mini', attrs={'data-stock': True})
            stock = self._extract_stock(stock_elem)
            
            # Extract brand
            brand = self._extract_brand(product_container)
            
            # Extract SKU from meta tag
            sku = ''
            sku_meta = soup.find('meta', itemprop='sku')
            if sku_meta:
                sku = sku_meta.get('content', '')
            
            # Determine component type from URL or name
            component_type = self._determine_component_type(url, name)
            
            # Create product dict
            product = self.create_product_dict(
                name=name,
                price_usd=price_data.get('price_usd', 0),
                price_local=price_data.get('price_local', 0),
                currency='PEN',
                stock=stock,
                brand=brand,
                sku=sku,
                source_url=url,
                image_url=image_url,
                component_type=component_type
            )
            
            return product
            
        except Exception as e:
            print(f"❌ Error scraping product {url}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def scrape_category_page(self, url: str, max_pages: Optional[int] = None) -> List[Dict]:
        """
        Scrapes all products from a category page
        
        Args:
            url: Category page URL
            max_pages: Maximum number of pages to scrape (None = all pages)
            
        Returns:
            List of product dictionaries
        """
        all_products = []
        current_page = 1
        
        print(f"\n🔍 Scraping ComputerShop category: {url}")
        
        while True:
            # Stop if max_pages reached
            if max_pages and current_page > max_pages:
                print(f"   ⚠️ Límite de {max_pages} páginas alcanzado")
                break
            
            # Build page URL
            if current_page == 1:
                page_url = url
            else:
                page_url = f"{url}?page={current_page}"
            
            print(f"\n   📄 Página {current_page}: {page_url}")
            
            # Fetch page
            soup = self.fetch_page(page_url, wait_time=3)
            if not soup:
                print(f"   ❌ Error fetching page {current_page}")
                break
            
            # Find all product containers
            product_containers = soup.find_all('div', class_='product-container')
            
            if not product_containers:
                print(f"   ℹ️ No más productos encontrados en página {current_page}")
                break
            
            print(f"   ✅ {len(product_containers)} productos encontrados")
            
            # Extract products from current page
            page_products = 0
            for container in product_containers:
                product = self._extract_product_from_container(container, url)
                if product:
                    all_products.append(product)
                    page_products += 1
            
            print(f"   💾 {page_products} productos extraídos exitosamente")
            
            # Check if there's a next page
            pagination = soup.find('nav', class_='pagination')
            if not pagination:
                print(f"   ℹ️ No hay paginación, última página alcanzada")
                break
            
            next_link = pagination.find('a', class_='next')
            if not next_link or 'disabled' in next_link.get('class', []):
                print(f"   ℹ️ Última página alcanzada")
                break
            
            current_page += 1
            time.sleep(2)  # Be respectful to the server
        
        print(f"\n✅ Total de productos scrapeados: {len(all_products)}")
        return all_products
    
    def _extract_product_from_container(self, container, category_url: str) -> Optional[Dict]:
        """
        Extracts product information from a product container
        
        Args:
            container: BeautifulSoup element with class 'product-container'
            category_url: Category URL for component type detection
            
        Returns:
            Product dictionary or None
        """
        try:
            # Extract product name
            name_elem = container.find('h5', class_='product-name')
            if not name_elem or not name_elem.find('a'):
                return None
            
            name_link = name_elem.find('a')
            name = name_link.get_text(strip=True)
            product_url = name_link.get('href', '')
            
            # Make URL absolute
            if product_url and not product_url.startswith('http'):
                product_url = self.base_url + product_url
            
            # Extract image URL
            img_elem = container.find('img', class_='img-fluid')
            image_url = img_elem.get('src', '') if img_elem else ''
            
            # Extract price
            price_elem = container.find('span', class_='product-price')
            price_data = self._extract_price(price_elem)
            
            # Extract stock
            stock_elem = container.find('span', class_='stock-mini', attrs={'data-stock': True})
            stock = self._extract_stock(stock_elem)
            
            # Extract brand
            brand = self._extract_brand(container)
            
            # Extract SKU from container parent (if available)
            sku = ''
            sku_meta = container.find_parent('div', class_='product-miniature')
            if sku_meta:
                sku_elem = sku_meta.find('meta', itemprop='sku')
                if sku_elem:
                    sku = sku_elem.get('content', '')
            
            # Determine component type
            component_type = self._determine_component_type(category_url, name)
            
            # Create product dict
            product = self.create_product_dict(
                name=name,
                price_usd=price_data.get('price_usd', 0),
                price_local=price_data.get('price_local', 0),
                currency='PEN',
                stock=stock,
                brand=brand,
                sku=sku,
                source_url=product_url,
                image_url=image_url,
                component_type=component_type
            )
            
            return product
            
        except Exception as e:
            print(f"      ⚠️ Error extracting product: {e}")
            return None
    
    def _extract_price(self, price_elem) -> Dict:
        """
        Extracts price from price element
        Format: "$&nbsp;26,00&nbsp;&nbsp;&nbsp;(S/&nbsp;89,70)"
        
        Returns:
            Dict with price_usd and price_local
        """
        if not price_elem:
            return {'price_usd': 0, 'price_local': 0}
        
        price_text = price_elem.get_text(strip=True)
        
        # Remove HTML entities
        price_text = price_text.replace('\xa0', ' ').replace('&nbsp;', ' ')
        
        # Extract USD price: $ 26,00
        usd_match = re.search(r'\$\s*([\d,\.]+)', price_text)
        price_usd = 0
        if usd_match:
            usd_str = self._normalize_price_number(usd_match.group(1))
            try:
                price_usd = float(usd_str)
            except:
                pass
        
        # Extract PEN price: S/ 89,70
        pen_match = re.search(r'S/\s*([\d,\.]+)', price_text)
        price_local = 0
        if pen_match:
            pen_str = self._normalize_price_number(pen_match.group(1))
            try:
                price_local = float(pen_str)
            except:
                pass
        
        return {
            'price_usd': price_usd,
            'price_local': price_local
        }
    
    def _extract_stock(self, stock_elem) -> str:
        """
        Extracts stock information
        Format: "Stock: >20" or "Últimas unidades en stock"
        
        Returns:
            Stock string in standard format
        """
        if not stock_elem:
            # Check for availability message
            return '0'
        
        stock_text = stock_elem.get_text(strip=True)
        
        # Remove "Stock:" prefix
        stock_text = stock_text.replace('Stock:', '').strip()
        
        # Handle different formats
        if '>' in stock_text or '&gt;' in stock_text:
            # "Stock: >20" or "Stock: &gt;20"
            stock_text = stock_text.replace('&gt;', '>').replace('>', '+')
            # Extract number
            num_match = re.search(r'\+(\d+)', stock_text)
            if num_match:
                return f'+{num_match.group(1)}'
            return '+10'
        
        # Try to extract exact number
        num_match = re.search(r'(\d+)', stock_text)
        if num_match:
            return num_match.group(1)
        
        return '0'
    
    def _extract_brand(self, container) -> str:
        """
        Extracts brand from product container
        Format: "Marca: LIAN LI"
        
        Returns:
            Brand name
        """
        # Look for brand in stock-mini span
        brand_elems = container.find_all('span', class_='stock-mini')
        for elem in brand_elems:
            text = elem.get_text(strip=True)
            if 'Marca:' in text:
                brand = text.replace('Marca:', '').strip()
                return brand
        
        # Fallback: extract from product name
        name_elem = container.find('h5', class_='product-name')
        if name_elem:
            name = name_elem.get_text(strip=True)
            return self.extract_brand_from_name(name)
        
        return 'Unknown'
    
    def _determine_component_type(self, url: str, name: str) -> str:
        """
        Determines component type from URL and name
        
        Args:
            url: Product or category URL
            name: Product name
            
        Returns:
            Component type string
        """
        url_lower = url.lower()
        name_lower = name.lower()
        
        # Map URL patterns to component types
        if 'placa' in url_lower or 'motherboard' in url_lower:
            return 'placas-madre'
        elif 'procesador' in url_lower or 'cpu' in url_lower:
            return 'procesadores'
        elif 'memoria' in url_lower or 'ram' in url_lower:
            return 'memorias-ram'
        elif 'almacenamiento' in url_lower or 'disco' in url_lower or 'ssd' in url_lower:
            return 'almacenamiento'
        elif 'tarjeta' in url_lower or 'video' in url_lower or 'grafica' in url_lower:
            return 'tarjetas-video'
        
        # Fallback: use base class method
        return self.identify_component_type(name, '')


def test_scraper():
    """Test function for the ComputerShop scraper"""
    scraper = ComputerShopScraper(use_selenium=True)
    
    print("\n" + "="*70)
    print("🧪 TESTING COMPUTERSHOP SCRAPER")
    print("="*70)
    
    # Test category scraping (only first page)
    test_url = 'https://computershopperu.com/categoria/39-procesadores'
    print(f"\n📦 Testing category scrape: {test_url}")
    
    products = scraper.scrape_category_page(test_url, max_pages=1)
    
    if products:
        print(f"\n✅ Found {len(products)} products")
        print("\n📦 Sample product:")
        sample = products[0]
        print(f"   Name: {sample['name']}")
        print(f"   Price USD: ${sample['price_usd']}")
        print(f"   Price PEN: S/{sample['price_local']}")
        print(f"   Stock: {sample['stock']}")
        print(f"   Brand: {sample['brand']}")
        print(f"   SKU: {sample['sku']}")
        print(f"   Type: {sample['component_type']}")
        print(f"   URL: {sample['source_url']}")
        print(f"   Image: {'✅' if sample['image_url'] else '❌'}")
    else:
        print("\n❌ No products found")
    
    scraper.close_selenium()


if __name__ == "__main__":
    test_scraper()
