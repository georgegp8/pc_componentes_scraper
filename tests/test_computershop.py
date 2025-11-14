"""
Script de prueba rápida para ComputerShop scraper
"""
import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.computershop.scraper import ComputerShopScraper

def test_quick():
    """Test rápido del scraper de ComputerShop"""
    
    print("\n" + "="*70)
    print("🧪 TEST RÁPIDO - COMPUTERSHOP SCRAPER")
    print("="*70)
    
    scraper = ComputerShopScraper(use_selenium=True)
    
    # Test con primera página de procesadores
    test_url = 'https://computershopperu.com/categoria/39-procesadores'
    
    print(f"\n📦 Testeando scraping de: {test_url}")
    print(f"   (Solo primera página para prueba rápida)")
    
    products = scraper.scrape_category_page(test_url, max_pages=1)
    
    if not products:
        print("\n❌ No se encontraron productos")
        scraper.close_selenium()
        return False
    
    print(f"\n✅ {len(products)} productos encontrados")
    
    # Verificar calidad de datos
    with_price = sum(1 for p in products if p.get('price_usd', 0) > 0)
    with_image = sum(1 for p in products if p.get('image_url'))
    with_stock = sum(1 for p in products if p.get('stock') and p.get('stock') != '0')
    with_brand = sum(1 for p in products if p.get('brand') and p.get('brand') != 'Unknown')
    with_sku = sum(1 for p in products if p.get('sku'))
    
    total = len(products)
    
    print(f"\n📊 Calidad de datos:")
    print(f"   Con precio USD: {with_price}/{total} ({with_price/total*100:.1f}%)")
    print(f"   Con imagen: {with_image}/{total} ({with_image/total*100:.1f}%)")
    print(f"   Con stock: {with_stock}/{total} ({with_stock/total*100:.1f}%)")
    print(f"   Con marca: {with_brand}/{total} ({with_brand/total*100:.1f}%)")
    print(f"   Con SKU: {with_sku}/{total} ({with_sku/total*100:.1f}%)")
    
    # Mostrar muestra de productos
    print(f"\n{'='*70}")
    print("📦 MUESTRA DE PRODUCTOS")
    print('='*70)
    
    for i, product in enumerate(products[:3], 1):
        print(f"\n--- Producto #{i} ---")
        print(f"Nombre: {product.get('name', 'N/A')[:60]}...")
        print(f"Precio: ${product.get('price_usd', 0)} / S/{product.get('price_local', 0)}")
        print(f"Stock: {product.get('stock', 'N/A')}")
        print(f"Marca: {product.get('brand', 'N/A')}")
        print(f"SKU: {product.get('sku', 'N/A')}")
        print(f"Tipo: {product.get('component_type', 'N/A')}")
        print(f"URL: {product.get('source_url', 'N/A')[:60]}...")
        print(f"Imagen: {'✅' if product.get('image_url') else '❌'}")
    
    # Verificar éxito
    success_rate = (with_price / total * 100) if total > 0 else 0
    
    print(f"\n{'='*70}")
    if success_rate >= 80:
        print(f"✅ TEST EXITOSO - Tasa de éxito: {success_rate:.1f}%")
        print(f"✅ El scraper está funcionando correctamente")
    elif success_rate >= 50:
        print(f"⚠️ TEST PARCIAL - Tasa de éxito: {success_rate:.1f}%")
        print(f"⚠️ Algunos productos sin datos completos")
    else:
        print(f"❌ TEST FALLIDO - Tasa de éxito: {success_rate:.1f}%")
        print(f"❌ Revisar el scraper")
    
    print('='*70)
    
    scraper.close_selenium()
    
    return success_rate >= 80


if __name__ == "__main__":
    success = test_quick()
    sys.exit(0 if success else 1)
