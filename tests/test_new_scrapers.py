"""
Prueba de scrapers MemoryKings y PCImpacto
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers.memorykings_scraper import MemoryKingsScraper
from scrapers.pcimpacto_scraper import PCImpactoScraper

def test_memorykings():
    """Prueba scraper de MemoryKings"""
    
    print("🧪 PROBANDO MEMORYKINGS")
    print("=" * 70)
    
    scraper = MemoryKingsScraper(use_selenium=True)
    
    # URL de prueba - Procesadores
    test_url = "https://www.memorykings.pe/categoria-producto/procesadores/"
    
    print(f"\n📄 URL: {test_url}")
    print("-" * 70)
    
    try:
        # Probar quick scrape (desde listado)
        products = scraper.scrape_category_quick(test_url)
        
        if products:
            print(f"\n✅ Encontrados {len(products)} productos")
            
            # Mostrar primeros 3
            for i, product in enumerate(products[:3], 1):
                print(f"\n{i}. {product['name'][:60]}")
                print(f"   💰 USD: ${product['price_usd']:.2f}")
                if product.get('price_local'):
                    print(f"   💰 PEN: S/{product['price_local']:.2f}")
                print(f"   📦 Stock: {product.get('stock', 'N/A')}")
                print(f"   🖼️  Imagen: {'✅' if product.get('image_url') else '❌'}")
        else:
            print("⚠️ No se encontraron productos")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        scraper.close_selenium()

def test_pcimpacto():
    """Prueba scraper de PCImpacto"""
    
    print("\n\n🧪 PROBANDO PCIMPACTO")
    print("=" * 70)
    
    scraper = PCImpactoScraper(use_selenium=True)
    
    # URL de prueba - Procesadores
    test_url = "https://www.impacto.com.pe/procesadores"
    
    print(f"\n📄 URL: {test_url}")
    print("-" * 70)
    
    try:
        # Probar quick scrape
        products = scraper.scrape_category_quick(test_url)
        
        if products:
            print(f"\n✅ Encontrados {len(products)} productos")
            
            # Mostrar primeros 3
            for i, product in enumerate(products[:3], 1):
                print(f"\n{i}. {product['name'][:60]}")
                print(f"   💰 USD: ${product['price_usd']:.2f}")
                if product.get('price_local'):
                    print(f"   💰 PEN: S/{product['price_local']:.2f}")
                print(f"   📦 Stock: {product.get('stock', 'N/A')}")
                print(f"   🖼️  Imagen: {'✅' if product.get('image_url') else '❌'}")
        else:
            print("⚠️ No se encontraron productos")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        scraper.close_selenium()

if __name__ == "__main__":
    test_memorykings()
    test_pcimpacto()
    
    print("\n" + "=" * 70)
    print("✅ PRUEBAS COMPLETADAS")
    print("=" * 70)
