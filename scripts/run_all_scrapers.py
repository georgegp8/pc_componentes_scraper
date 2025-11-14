"""
Script unificado para ejecutar todos los scrapers
Ejecuta SercoPlus y MemoryKings y guarda resultados en sus respectivas carpetas
"""
import sys
import os
from datetime import datetime

# Agregar las rutas de los scrapers al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scrapers', 'memorykings'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scrapers', 'sercoplus'))

from scrapers.memorykings.scraper import MemoryKingsScraper
from scrapers.sercoplus.scraper import SercoPlusScraper
import json

def scrape_memorykings():
    """Ejecuta scraper de MemoryKings"""
    print("\n" + "="*80)
    print("🏪 MEMORYKINGS - Iniciando scraping...")
    print("="*80)
    
    scraper = MemoryKingsScraper()
    
    MAX_LISTADOS = 20
    MAX_PRODUCTS = 30
    
    all_results = {}
    total_products = 0
    
    for category_key in scraper.categories.keys():
        products = scraper.scrape_category(category_key, MAX_LISTADOS, MAX_PRODUCTS)
        all_results[category_key] = products
        total_products += len(products)
        print(f"   ✅ {category_key}: {len(products)} productos")
    
    # Guardar resultados
    output_dir = os.path.join('scrapers', 'memorykings')
    output_file = os.path.join(output_dir, 'products.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'store': 'memorykings',
            'total_products': total_products,
            'categories': all_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 MemoryKings: {total_products} productos guardados en {output_file}")
    return total_products, all_results

def scrape_sercoplus():
    """Ejecuta scraper de SercoPlus"""
    print("\n" + "="*80)
    print("🏪 SERCOPLUS - Iniciando scraping...")
    print("="*80)
    
    scraper = SercoPlusScraper()
    
    all_results = {}
    total_products = 0
    
    for category_key, category_name in scraper.categories.items():
        print(f"\n📦 Scraping: {category_name}")
        products = scraper.scrape_category(category_key)
        all_results[category_key] = products
        total_products += len(products)
        print(f"   ✅ {len(products)} productos")
    
    # Guardar resultados
    output_dir = os.path.join('scrapers', 'sercoplus')
    output_file = os.path.join(output_dir, 'products.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'store': 'sercoplus',
            'total_products': total_products,
            'categories': all_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 SercoPlus: {total_products} productos guardados en {output_file}")
    return total_products, all_results

def main():
    """Ejecuta todos los scrapers"""
    print("\n" + "="*80)
    print("🚀 SCRAPING UNIFICADO - TODAS LAS TIENDAS")
    print("="*80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Tiendas: MemoryKings, SercoPlus")
    
    results = {}
    
    # Scrape SercoPlus
    try:
        total_serco, data_serco = scrape_sercoplus()
        results['sercoplus'] = {
            'total': total_serco,
            'success': True
        }
    except Exception as e:
        print(f"\n❌ Error en SercoPlus: {e}")
        results['sercoplus'] = {
            'total': 0,
            'success': False,
            'error': str(e)
        }
    
    # Scrape MemoryKings
    try:
        total_mk, data_mk = scrape_memorykings()
        results['memorykings'] = {
            'total': total_mk,
            'success': True
        }
    except Exception as e:
        print(f"\n❌ Error en MemoryKings: {e}")
        results['memorykings'] = {
            'total': 0,
            'success': False,
            'error': str(e)
        }
    
    # Resumen final
    print("\n\n" + "="*80)
    print("✅ SCRAPING COMPLETADO - RESUMEN FINAL")
    print("="*80)
    
    total_all = 0
    for store, info in results.items():
        status = "✅" if info['success'] else "❌"
        print(f"{status} {store.upper():15s}: {info['total']:4d} productos")
        total_all += info['total']
    
    print(f"\n{'='*80}")
    print(f"📦 TOTAL GENERAL: {total_all} productos")
    print("="*80)
    
    # Guardar resumen
    with open('scraping_summary.json', 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'stores': results,
            'total_products': total_all
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resumen guardado en: scraping_summary.json")

if __name__ == "__main__":
    main()
