"""
Script mejorado para ejecutar todos los scrapers incluyendo ComputerShop
Ejecuta todas las tiendas y consolida resultados
"""
import sys
import os
from datetime import datetime
import subprocess

def run_scraper(store_name, scraper_path):
    """
    Ejecuta un scraper específico
    
    Args:
        store_name: Nombre de la tienda
        scraper_path: Path al script run.py del scraper
    
    Returns:
        bool: True si exitoso, False si falló
    """
    print(f"\n{'='*80}")
    print(f"🏪 {store_name.upper()} - Iniciando scraping...")
    print('='*80)
    
    try:
        # Change to scraper directory
        scraper_dir = os.path.dirname(scraper_path)
        original_dir = os.getcwd()
        
        os.chdir(scraper_dir)
        
        # Run the scraper
        result = subprocess.run(
            [sys.executable, 'run.py'],
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutes timeout
        )
        
        # Return to original directory
        os.chdir(original_dir)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        if result.returncode == 0:
            print(f"\n✅ {store_name} scraping completado exitosamente")
            return True
        else:
            print(f"\n❌ Error en {store_name} scraping")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"\n⏱️ Timeout en {store_name} scraping (30 minutos)")
        os.chdir(original_dir)
        return False
    except Exception as e:
        print(f"\n❌ Error ejecutando {store_name}: {e}")
        os.chdir(original_dir)
        return False

def load_to_database(store_name, loader_path):
    """
    Carga productos a la base de datos
    
    Args:
        store_name: Nombre de la tienda
        loader_path: Path al script load_to_db.py
    
    Returns:
        bool: True si exitoso, False si falló
    """
    print(f"\n📥 Cargando {store_name} a base de datos...")
    
    try:
        loader_dir = os.path.dirname(loader_path)
        original_dir = os.getcwd()
        
        os.chdir(loader_dir)
        
        result = subprocess.run(
            [sys.executable, 'load_to_db.py'],
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes timeout
        )
        
        os.chdir(original_dir)
        
        if result.stdout:
            print(result.stdout)
        
        if result.returncode == 0:
            print(f"✅ {store_name} cargado a BD exitosamente")
            return True
        else:
            print(f"❌ Error cargando {store_name} a BD")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error cargando {store_name}: {e}")
        os.chdir(original_dir)
        return False

def main():
    """Ejecuta todos los scrapers y carga a BD"""
    
    print("\n" + "="*80)
    print("🚀 SCRAPING UNIFICADO - TODAS LAS TIENDAS")
    print("="*80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Define stores and their paths
    stores = [
        {
            'name': 'SercoPlus',
            'scraper': 'scrapers/sercoplus/run.py',
            'loader': 'scripts/load_sercoplus_to_db.py'
        },
        {
            'name': 'MemoryKings',
            'scraper': 'scrapers/memorykings/run.py',
            'loader': 'scripts/load_memorykings_to_db.py'
        },
        {
            'name': 'PCImpacto',
            'scraper': 'scrapers/impacto/run.py',
            'loader': 'scrapers/impacto/load_to_db.py'
        },
        {
            'name': 'CycComputer',
            'scraper': 'scrapers/cyccomputer/run.py',
            'loader': 'scrapers/cyccomputer/load_to_db.py'
        },
        {
            'name': 'ComputerShop',
            'scraper': 'scrapers/computershop/run.py',
            'loader': 'scrapers/computershop/load_to_db.py'
        }
    ]
    
    print(f"Tiendas a procesar: {len(stores)}")
    for store in stores:
        print(f"  - {store['name']}")
    
    results = {}
    
    # Process each store
    for store in stores:
        store_name = store['name']
        
        # Check if scraper exists
        if not os.path.exists(store['scraper']):
            print(f"\n⚠️ Scraper no encontrado para {store_name}: {store['scraper']}")
            results[store_name] = {
                'scrape_success': False,
                'load_success': False,
                'error': 'Scraper not found'
            }
            continue
        
        # Run scraper
        scrape_success = run_scraper(store_name, store['scraper'])
        
        # Load to database if scraping successful
        load_success = False
        if scrape_success and os.path.exists(store['loader']):
            load_success = load_to_database(store_name, store['loader'])
        elif scrape_success:
            print(f"⚠️ Loader no encontrado para {store_name}: {store['loader']}")
        
        results[store_name] = {
            'scrape_success': scrape_success,
            'load_success': load_success
        }
    
    # Final summary
    print("\n\n" + "="*80)
    print("✅ PROCESAMIENTO COMPLETADO - RESUMEN FINAL")
    print("="*80)
    
    print(f"\n{'Tienda':<20} {'Scraping':<15} {'Carga BD':<15}")
    print("-" * 80)
    
    total_success = 0
    for store_name, result in results.items():
        scrape_icon = "✅" if result['scrape_success'] else "❌"
        load_icon = "✅" if result['load_success'] else "❌"
        
        scrape_text = f"{scrape_icon} {'Exitoso' if result['scrape_success'] else 'Fallido'}"
        load_text = f"{load_icon} {'Exitoso' if result['load_success'] else 'Fallido'}"
        
        print(f"{store_name:<20} {scrape_text:<15} {load_text:<15}")
        
        if result['scrape_success'] and result['load_success']:
            total_success += 1
    
    print("-" * 80)
    print(f"\n📊 Tiendas completadas exitosamente: {total_success}/{len(stores)}")
    
    # Check database stats
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from database import Database
        
        db = Database('pc_prices.db')
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT store, COUNT(*) as count 
            FROM products 
            WHERE is_active = 1
            GROUP BY store
            ORDER BY count DESC
        """)
        
        print(f"\n📈 Productos en base de datos:")
        total_db = 0
        for row in cursor.fetchall():
            count = row['count']
            total_db += count
            print(f"  - {row['store']:<20}: {count:>5} productos")
        
        print(f"  {'TOTAL':<20}: {total_db:>5} productos")
        
        conn.close()
        
    except Exception as e:
        print(f"\n⚠️ No se pudo obtener estadísticas de BD: {e}")
    
    print("\n" + "="*80)
    print("✅ Proceso completado")
    print("="*80)


if __name__ == "__main__":
    main()
