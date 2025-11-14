"""
Scraping completo de SercoPlus con imágenes y stock
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers.sercoplus_scraper import SercoPlusScraper
from database import Database
import time

def scrape_all_categories():
    """Scrapea todas las categorías de SercoPlus"""
    
    categories = [
        ("Procesadores", "https://sercoplus.com/37-procesadores"),
        ("Procesadores Intel", "https://sercoplus.com/52-procesadores-intel"),
        ("Procesadores AMD", "https://sercoplus.com/36-procesadores-amd"),
        ("Tarjetas de Video", "https://sercoplus.com/32-tarjeta-de-video"),
        ("Memoria RAM", "https://sercoplus.com/55-memorias-ram"),
        ("RAM PC", "https://sercoplus.com/87-memoria-ram-pc"),
        ("Almacenamiento", "https://sercoplus.com/53-almacenamiento"),
    ]
    
    print("🚀 SCRAPING COMPLETO DE SERCOPLUS")
    print("=" * 70)
    print("📦 Capturando: URLs de imágenes + Stock numérico + Precios USD/PEN")
    print("=" * 70)
    
    scraper = SercoPlusScraper(use_selenium=True)
    db = Database()
    
    total_products = 0
    total_with_images = 0
    
    try:
        for i, (name, url) in enumerate(categories, 1):
            print(f"\n{'='*70}")
            print(f"📂 [{i}/{len(categories)}] {name}")
            print(f"🔗 {url}")
            print('-'*70)
            
            try:
                products = scraper.scrape_category_page(url)
                
                if products:
                    # Save to database
                    saved_count = 0
                    with_images = 0
                    
                    for product in products:
                        result = db.insert_product(product)
                        if result:
                            saved_count += 1
                            if product.get('image_url'):
                                with_images += 1
                    
                    total_products += saved_count
                    total_with_images += with_images
                    
                    print(f"✅ Guardados: {saved_count} productos")
                    print(f"🖼️  Con imagen: {with_images}/{saved_count} ({with_images/saved_count*100:.0f}%)")
                else:
                    print("⚠️ No se encontraron productos")
                
                # Delay between categories
                if i < len(categories):
                    time.sleep(2)
                    
            except Exception as e:
                print(f"❌ Error en categoría {name}: {e}")
                continue
        
        print("\n" + "="*70)
        print("📊 RESUMEN FINAL")
        print("="*70)
        print(f"✅ Total productos guardados: {total_products}")
        if total_products > 0:
            print(f"🖼️  Total con imágenes: {total_with_images} ({total_with_images/total_products*100:.1f}%)")
        print(f"📂 Categorías procesadas: {len(categories)}")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        scraper.close_selenium()

if __name__ == "__main__":
    scrape_all_categories()
