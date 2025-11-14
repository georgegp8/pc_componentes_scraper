"""
Script para cargar productos de MemoryKings desde JSON a la base de datos
"""
import json
import sys
from database import Database
from datetime import datetime

def load_memorykings_to_db():
    """Carga productos de MemoryKings JSON a la base de datos"""
    
    print("\n" + "="*80)
    print("📥 CARGANDO PRODUCTOS DE MEMORYKINGS A LA BASE DE DATOS")
    print("="*80 + "\n")
    
    # Inicializar base de datos
    db = Database()
    db.init_db()
    
    # Leer JSON
    json_path = 'scrapers/memorykings/products.json'
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ No se encontró: {json_path}")
        print("   Ejecuta primero: cd scrapers/memorykings && python run.py")
        return False
    
    print(f"📄 Archivo: {json_path}")
    print(f"📅 Timestamp: {data.get('timestamp')}")
    print(f"📦 Total productos: {data.get('total_products')}\n")
    
    # Insertar productos por categoría
    total_inserted = 0
    total_updated = 0
    total_skipped = 0
    
    for category, products in data['categories'].items():
        print(f"\n📂 Categoría: {category.upper()} ({len(products)} productos)")
        
        for product in products:
            # Preparar datos para inserción
            product_data = {
                'name': product['name'],
                'normalized_name': product.get('normalized_name', ''),
                'component_type': category,
                'brand': product.get('brand', ''),
                'sku': product.get('sku', ''),
                'price_usd': product.get('price_usd', 0),
                'price_local': product.get('price_local', 0),
                'currency': product.get('currency', 'PEN'),
                'stock': product.get('stock', 'unknown'),
                'store': 'memorykings',
                'source_url': product.get('source_url', ''),
                'image_url': product.get('image_url', ''),
                'is_active': True,
                'last_scraped': datetime.now().isoformat()
            }
            
            # Intentar insertar
            result = db.insert_product(product_data)
            if result:
                total_inserted += 1
            else:
                # Producto ya existe, intentar actualizar
                existing = db.get_products(
                    0, 1,
                    component_type=category,
                    store='memorykings'
                )
                # Por ahora contar como skipped
                total_skipped += 1
        
        print(f"   ✅ {category}: Procesados")
    
    print("\n" + "="*80)
    print("✅ CARGA COMPLETADA")
    print("="*80)
    print(f"✅ Insertados: {total_inserted}")
    print(f"⚠️ Saltados (duplicados): {total_skipped}")
    print(f"📊 Total procesados: {total_inserted + total_skipped}\n")
    
    # Verificar
    print("Verificando datos en BD...")
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT component_type, COUNT(*) as count
        FROM products
        WHERE store = 'memorykings' AND is_active = 1
        GROUP BY component_type
    """)
    
    print("\n📊 Productos por categoría en BD:")
    for row in cursor.fetchall():
        print(f"   - {row['component_type']}: {row['count']}")
    
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM products
        WHERE store = 'memorykings' AND is_active = 1
    """)
    total_db = cursor.fetchone()['total']
    print(f"\n📦 Total MemoryKings en BD: {total_db}")
    
    conn.close()
    
    return True

if __name__ == "__main__":
    success = load_memorykings_to_db()
    if success:
        print("\n✅ Ahora puedes consultar los productos vía API:")
        print("   http://localhost:8000/api/stores/memorykings/products")
        print("   http://localhost:8000/api/stores/memorykings/stats\n")
    else:
        sys.exit(1)
