"""
Reset and Configure Scraping Tasks
Limpia la base de datos y configura las tareas de scraping correctamente
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database
from scheduler import ScrapingScheduler
from config import config

def main():
    print("="*60)
    print("  CONFIGURAR TAREAS DE SCRAPING")
    print("="*60)
    print()
    
    db = Database(config.DATABASE_PATH)
    scheduler = ScrapingScheduler(db)
    
    # Limpiar datos existentes
    print("¿Deseas limpiar los productos existentes? (s/n)")
    response = input("> ").lower().strip()
    
    if response in ['s', 'si', 'yes', 'y']:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products")
        cursor.execute("DELETE FROM price_history")
        cursor.execute("DELETE FROM product_matches")
        conn.commit()
        conn.close()
        print("✅ Productos limpiados")
    
    print()
    print("¿Deseas limpiar las tareas programadas existentes? (s/n)")
    response = input("> ").lower().strip()
    
    if response in ['s', 'si', 'yes', 'y']:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM scraping_schedule")
        cursor.execute("DELETE FROM scraping_logs")
        conn.commit()
        conn.close()
        print("✅ Tareas limpiadas")
    
    # Agregar nuevas tareas
    print()
    print("📋 Agregando tareas de scraping...")
    print()
    
    tasks = [
        # SercoPlus - Procesadores (URLs VERIFICADAS - Nov 2025)
        ('SercoPlus', 'https://sercoplus.com/37-procesadores', 'Procesadores (Todos)', 24),
        ('SercoPlus', 'https://sercoplus.com/52-procesadores-intel', 'Procesadores Intel', 24),
        ('SercoPlus', 'https://sercoplus.com/36-procesadores-amd', 'Procesadores AMD', 24),
        
        # SercoPlus - Tarjetas Gráficas (46 productos verificados)
        ('SercoPlus', 'https://sercoplus.com/32-tarjeta-de-video', 'Tarjetas de Video', 24),
        
        # SercoPlus - Memorias RAM (67 productos verificados)
        ('SercoPlus', 'https://sercoplus.com/55-memorias-ram', 'Memorias RAM', 24),
        ('SercoPlus', 'https://sercoplus.com/87-memoria-ram-pc', 'Memorias RAM PC', 24),
        
        # SercoPlus - Almacenamiento
        ('SercoPlus', 'https://sercoplus.com/53-almacenamiento', 'Almacenamiento', 24),
        
        # Puedes agregar MemoryKings y PCImpacto cuando tengas sus URLs
        # ('MemoryKings', 'URL', 'Categoría', 24),
        # ('PCImpacto', 'URL', 'Categoría', 24),
    ]
    
    added = 0
    for store_name, url, category, frequency in tasks:
        if scheduler.add_scraping_task(store_name, url, category, frequency):
            print(f"  ✓ {store_name} - {category}")
            added += 1
        else:
            print(f"  ⚠ Ya existe: {store_name} - {category}")
    
    print()
    print(f"✅ {added} tareas agregadas")
    print()
    
    # Opción de ejecutar scraping
    print("¿Deseas ejecutar el scraping ahora? (esto puede tomar varios minutos)")
    print("Se scrapearán todas las categorías configuradas")
    response = input("(s/n): ").lower().strip()
    
    if response in ['s', 'si', 'yes', 'y']:
        print()
        print("🚀 Iniciando scraping...")
        print("=" * 60)
        scheduler.check_and_run_tasks()
        print("=" * 60)
        print("✅ Scraping completado")
        
        # Mostrar estadísticas
        stats = db.get_statistics()
        print()
        print("📊 Estadísticas:")
        print(f"  Total de productos: {stats['total_products']}")
        print(f"  Tiendas: {len(stats['products_by_store'])}")
        for store_stat in stats['products_by_store']:
            print(f"    - {store_stat['store']}: {store_stat['count']} productos")
    else:
        print()
        print("⏩ Scraping omitido")
        print("   Las tareas se ejecutarán automáticamente cada 24h")
        print("   O ejecuta: python main.py y usa POST /api/schedule/run-now")
    
    print()
    print("="*60)
    print("  ✓ CONFIGURACIÓN COMPLETA")
    print("="*60)
    print()
    print("Para iniciar el servidor API:")
    print("  python main.py")
    print()

if __name__ == "__main__":
    main()
