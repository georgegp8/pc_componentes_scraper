"""
Script para cargar productos de ComputerShop Peru a la base de datos
"""
import sys
import os
import json
from datetime import datetime

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import Database

def load_products_to_db(json_file='products.json', db_path='../../pc_prices.db'):
    """
    Carga productos desde JSON a la base de datos
    
    Args:
        json_file: Path al archivo JSON con productos
        db_path: Path a la base de datos SQLite
    """
    print("\n" + "="*70)
    print("📥 CARGANDO PRODUCTOS DE COMPUTERSHOP A BASE DE DATOS")
    print("="*70)
    
    # Check if JSON file exists
    if not os.path.exists(json_file):
        print(f"❌ Error: Archivo {json_file} no encontrado")
        print(f"   Ejecuta primero: python run.py")
        return
    
    # Load JSON data
    print(f"\n📂 Cargando datos desde: {json_file}")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
    print(f"   Total productos: {data.get('total_products', 0)}")
    
    # Initialize database
    db = Database(db_path)
    db.init_db()
    
    # Insert products
    total_inserted = 0
    total_updated = 0
    total_errors = 0
    
    categories = data.get('categories', {})
    
    for category_name, products in categories.items():
        print(f"\n📦 Procesando categoría: {category_name}")
        print(f"   Productos: {len(products)}")
        
        category_inserted = 0
        category_updated = 0
        category_errors = 0
        
        for i, product in enumerate(products, 1):
            try:
                # Check if product already exists
                existing = None
                if product.get('source_url'):
                    conn = db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT id, price_usd FROM products WHERE source_url = ?",
                        (product['source_url'],)
                    )
                    existing = cursor.fetchone()
                    conn.close()
                
                # Insert or update
                success = db.insert_product(product)
                
                if success:
                    if existing:
                        category_updated += 1
                        total_updated += 1
                    else:
                        category_inserted += 1
                        total_inserted += 1
                else:
                    category_errors += 1
                    total_errors += 1
                
                # Progress indicator
                if i % 10 == 0:
                    print(f"   Progreso: {i}/{len(products)} productos procesados...")
                    
            except Exception as e:
                print(f"   ⚠️ Error procesando producto {i}: {e}")
                category_errors += 1
                total_errors += 1
        
        print(f"   ✅ Insertados: {category_inserted}")
        print(f"   🔄 Actualizados: {category_updated}")
        if category_errors > 0:
            print(f"   ❌ Errores: {category_errors}")
    
    # Final summary
    print(f"\n{'='*70}")
    print(f"✅ CARGA COMPLETADA")
    print('='*70)
    print(f"\n📊 Resumen:")
    print(f"  Nuevos productos: {total_inserted}")
    print(f"  Productos actualizados: {total_updated}")
    print(f"  Total procesado: {total_inserted + total_updated}")
    if total_errors > 0:
        print(f"  ⚠️ Errores: {total_errors}")
    
    # Show database stats
    print(f"\n📈 Estadísticas de la base de datos:")
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Total products by store
    cursor.execute("""
        SELECT store, COUNT(*) as count 
        FROM products 
        WHERE is_active = 1
        GROUP BY store
        ORDER BY count DESC
    """)
    
    print(f"\n  Productos por tienda:")
    for row in cursor.fetchall():
        print(f"    - {row['store']}: {row['count']} productos")
    
    # ComputerShop products by category
    cursor.execute("""
        SELECT component_type, COUNT(*) as count 
        FROM products 
        WHERE store = 'computershop' AND is_active = 1
        GROUP BY component_type
        ORDER BY count DESC
    """)
    
    print(f"\n  ComputerShop por categoría:")
    for row in cursor.fetchall():
        print(f"    - {row['component_type']}: {row['count']} productos")
    
    conn.close()
    
    print(f"\n✅ Base de datos actualizada: {db_path}")


if __name__ == "__main__":
    load_products_to_db()
