"""
Script completo para scrapear SercoPlus - Todas las categorías
"""
from scraper import SercoPlusScraper
import json
from datetime import datetime
import os

def main():
    scraper = SercoPlusScraper(use_selenium=True)
    
    # Categorías de SercoPlus con URLs CORREGIDAS
    # Mismo orden que Impacto: placas-madre, procesadores, memorias-ram, almacenamiento, tarjetas-video
    categories = {
        'placas-madre': 'https://sercoplus.com/34-mainboard',
        'procesadores': 'https://sercoplus.com/37-procesadores',
        'memorias-ram': 'https://sercoplus.com/55-memorias-ram',
        'almacenamiento': 'https://sercoplus.com/53-almacenamiento',
        'tarjetas-video': 'https://sercoplus.com/32-tarjeta-de-video',
    }
    
    print("\n" + "="*70)
    print("🚀 SCRAPING COMPLETO DE SERCOPLUS")
    print("="*70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Categorías: {len(categories)}")
    
    # Scrape todas las categorías
    all_results = {}
    total_products = 0
    
    for category_key, category_url in categories.items():
        print(f"\n📦 Scraping: {category_key.upper()}")
        print(f"   URL: {category_url}")
        
        # Scrape category page (todas las páginas sin límite)
        products = scraper.scrape_category_page(category_url, max_pages=None)
        all_results[category_key] = products
        total_products += len(products)
        
        print(f"   ✅ {len(products)} productos scrapeados")
    
    # Resumen final
    print(f"\n\n{'='*70}")
    print(f"✅ SCRAPING COMPLETADO")
    print('='*70)
    print(f"\nTotal de productos: {total_products}")
    print(f"\nPor categoría:")
    for category, products in all_results.items():
        print(f"  - {category}: {len(products)} productos")
    
    # Estadísticas generales
    all_products_flat = []
    for products in all_results.values():
        all_products_flat.extend(products)
    
    if all_products_flat:
        with_price = sum(1 for p in all_products_flat if p.get('price_usd') or p.get('price_local'))
        with_image = sum(1 for p in all_products_flat if p.get('image_url'))
        with_stock = sum(1 for p in all_products_flat if p.get('stock'))
        
        print(f"\nCalidad de datos:")
        print(f"  Con precio: {with_price}/{total_products} ({with_price/total_products*100:.1f}%)")
        print(f"  Con imagen: {with_image}/{total_products} ({with_image/total_products*100:.1f}%)")
        print(f"  Con stock: {with_stock}/{total_products} ({with_stock/total_products*100:.1f}%)")
        
        # Guardar resultados
        output_file = 'products.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_products': total_products,
                'categories': all_results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados guardados en: {output_file}")
        
        # Mostrar muestra de cada categoría
        print(f"\n{'='*70}")
        print("📦 MUESTRA DE PRODUCTOS POR CATEGORÍA")
        print('='*70)
        
        for category, products in all_results.items():
            if products:
                print(f"\n--- {category.upper()} ---")
                sample = products[0]
                print(f"Nombre: {sample.get('name', '')[:70]}...")
                print(f"Precio: ${sample.get('price_usd', 0)} / S/{sample.get('price_local', 0)}")
                print(f"Stock: {sample.get('stock', 'N/A')}")
                print(f"Imagen: {'✅' if sample.get('image_url') else '❌'}")

if __name__ == "__main__":
    main()
