"""
Script para cargar productos de SercoPlus desde JSON a la base de datos
"""
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from database import Database
from datetime import datetime

def load_sercoplus_to_db():
    """Carga productos de SercoPlus JSON a la base de datos"""
    
    print("\n" + "="*80)
    print("📥 CARGANDO PRODUCTOS DE SERCOPLUS A LA BASE DE DATOS")
    print("="*80 + "\n")
    
    # Inicializar base de datos
    db = Database('pc_prices.db')
    db.init_db()
    
    # Leer JSON
    json_path = 'scrapers/sercoplus/products.json'
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ No se encontró: {json_path}")
        print("   Ejecuta primero: python scrapers/sercoplus/run.py")
        return False
    
    print(f"📄 Archivo: {json_path}")
    print(f"📅 Timestamp: {data.get('timestamp')}")
    print(f"📦 Total productos: {data.get('total_products')}\n\n")
    
    # Cargar por categoría
    categories = data.get('categories', {})
    inserted = 0
    skipped = 0
    
    for category_key, products in categories.items():
        print(f"📂 Categoría: {category_key.upper()} ({len(products)} productos)")
        
        for product in products:
            # Asegurar que tenga store
            product['store'] = 'sercoplus'
            
            # Usar el nombre de categoría como component_type
            product['component_type'] = category_key
            
            # Insertar o actualizar
            success = db.insert_product(product)
            if success:
                inserted += 1
            else:
                skipped += 1
        
        print(f"   ✅ {category_key}: Procesados\n")
    
    # Resumen
    print("\n" + "="*80)
    print("✅ CARGA COMPLETADA")
    print("="*80)
    print(f"✅ Insertados: {inserted}")
    print(f"⚠️ Saltados (duplicados): {skipped}")
    print(f"📊 Total procesados: {inserted + skipped}\n")
    
    # Verificar datos en BD
    print("Verificando datos en BD...\n")
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Por categoría
    cursor.execute("""
        SELECT component_type, COUNT(*) as count 
        FROM products 
        WHERE store = 'sercoplus'
        GROUP BY component_type
        ORDER BY count DESC
    """)
    
    print("📊 Productos por categoría en BD:")
    for row in cursor.fetchall():
        print(f"   - {row['component_type']}: {row['count']}")
    
    # Total
    cursor.execute("""
        SELECT COUNT(*) as count FROM products WHERE store = 'sercoplus'
    """)
    total = cursor.fetchone()['count']
    print(f"\n📦 Total SercoPlus en BD: {total}\n")
    
    conn.close()
    
    print("✅ Ahora puedes consultar los productos vía API:")
    print("   http://localhost:8000/api/stores/sercoplus/products")
    print("   http://localhost:8000/api/stores/sercoplus/stats\n")
    
    return True

if __name__ == "__main__":
    load_sercoplus_to_db()
