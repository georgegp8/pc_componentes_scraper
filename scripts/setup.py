"""
Setup Script - Initialize Database and Scraping Tasks
Run this after first installation to set up the system
"""

import sys
import os
import sqlite3

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database
from scheduler import ScrapingScheduler
from config import config

def check_and_migrate_database():
    """Check if database needs migration"""
    db_path = config.DATABASE_PATH
    
    if not os.path.exists(db_path):
        return True  # New database, no migration needed
    
    # Check if old schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'normalized_name' not in columns:
            conn.close()
            print("\n⚠️  Base de datos antigua detectada")
            print("    Se requiere migración al nuevo esquema")
            print()
            response = input("¿Deseas migrar automáticamente? (s/n): ").lower().strip()
            
            if response in ['s', 'si', 'yes', 'y']:
                print("\n🔄 Ejecutando migración...")
                os.system(f"{sys.executable} migrate_db.py")
                print()
                return True
            else:
                print("\n❌ Migración cancelada")
                print("   Opción 1: Ejecuta 'python migrate_db.py' manualmente")
                print("   Opción 2: Elimina 'pc_prices.db' para crear base nueva")
                return False
        
        conn.close()
        return True
        
    except Exception as e:
        conn.close()
        print(f"\n⚠️  Error verificando base de datos: {e}")
        return False

def main():
    print("="*60)
    print("  PC PRICE SCRAPER - SETUP")
    print("="*60)
    print()
    
    # Initialize database
    print("📊 Inicializando base de datos...")
    try:
        db = Database(config.DATABASE_PATH)
        db.init_db()
        print("✅ Base de datos lista")
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        print()
        print("Posibles soluciones:")
        print("  1. Ejecuta: python migrate_db.py")
        print("  2. O elimina 'pc_prices.db' para crear una nueva")
        sys.exit(1)
    
    # Initialize scheduler
    print("\n⏰ Configurando tareas programadas...")
    scheduler = ScrapingScheduler(db)
    
    # Add scraping tasks for common categories
    # NOTA: Puedes agregar más URLs manualmente después usando la API /api/schedule/add
    tasks_to_add = [
        # SercoPlus - Procesadores
        ('SercoPlus', 'https://sercoplus.com/765-cpu-1700-12va-generacion', 'Procesadores Intel Socket 1700', 24),
        ('SercoPlus', 'https://sercoplus.com/758-cpu-am4-ryzen-serie-3000-4000-5000', 'Procesadores AMD AM4', 24),
        ('SercoPlus', 'https://sercoplus.com/645-cpu-1200-10ma-generacion', 'Procesadores Intel Socket 1200', 24),
        
        # SercoPlus - Tarjetas Gráficas
        ('SercoPlus', 'https://sercoplus.com/759-tarjetas-de-video', 'Tarjetas Gráficas', 24),
        
        # SercoPlus - Memorias RAM
        ('SercoPlus', 'https://sercoplus.com/692-ram-pc-ddr4', 'Memorias DDR4', 24),
        ('SercoPlus', 'https://sercoplus.com/691-ram-pc-ddr5', 'Memorias DDR5', 24),
        
        # SercoPlus - Almacenamiento
        ('SercoPlus', 'https://sercoplus.com/677-ssd-m2-nvme', 'SSD M.2 NVMe', 24),
        ('SercoPlus', 'https://sercoplus.com/676-ssd-sata', 'SSD SATA', 24),
    ]
    
    added_count = 0
    for store_name, url, category, frequency in tasks_to_add:
        if scheduler.add_scraping_task(store_name, url, category, frequency):
            added_count += 1
            print(f"  ✓ {store_name} - {category}")
    
    print(f"\n✅ {added_count} tareas programadas agregadas")
    
    print("\n"+"="*60)
    print("  CONFIGURACIÓN COMPLETA")
    print("="*60)
    print("\n📝 Próximos pasos:")
    print("  1. Copia .env.example a .env y ajusta la configuración")
    print("  2. Ejecuta: python main.py")
    print("  3. Visita: http://localhost:8000/docs para la API")
    print("  4. Las tareas programadas se ejecutarán automáticamente\n")
    
    # Option to run initial scrape
    print("¿Deseas ejecutar un scraping inicial ahora? (esto puede tomar varios minutos)")
    response = input("Ingresa 'si' para continuar o 'no' para omitir: ").lower().strip()
    
    if response in ['si', 's', 'yes', 'y']:
        print("\n🚀 Ejecutando scraping inicial...")
        scheduler.check_and_run_tasks()
        print("\n✅ Scraping inicial completado")
    else:
        print("\n⏩ Scraping inicial omitido")
        print("   Las tareas se ejecutarán según su programación")

if __name__ == "__main__":
    main()
