"""
Verificar que los datos mejorados se guardaron correctamente
"""
from database import Database

db = Database()
conn = db.get_connection()
cursor = conn.cursor()

print("\n🔍 VERIFICANDO DATOS MEJORADOS EN BD")
print("="*80)

# Verificar productos con stock
cursor.execute("""
    SELECT name, stock, image_url, sku, brand
    FROM products
    WHERE store = 'memorykings' AND stock != 'unknown'
    LIMIT 5
""")

products = cursor.fetchall()
print(f"\n✅ Productos con stock capturado: ({len(products)} de muestra)\n")

for p in products:
    print(f"📦 {p['name'][:65]}")
    print(f"   📦 Stock: {p['stock']}")
    print(f"   🏷️ SKU: {p['sku']}")
    print(f"   🏢 Marca: {p['brand']}")
    print(f"   🖼️ Imagen: {p['image_url'][:75] if p['image_url'] else 'N/A'}...")
    print()

# Estadísticas de stock
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN stock != 'unknown' THEN 1 ELSE 0 END) as with_stock,
        SUM(CASE WHEN image_url IS NOT NULL AND image_url != '' THEN 1 ELSE 0 END) as with_image
    FROM products
    WHERE store = 'memorykings'
""")

stats = cursor.fetchone()
print("="*80)
print("📊 ESTADÍSTICAS DE CALIDAD:")
print(f"   Total productos: {stats['total']}")
print(f"   Con stock: {stats['with_stock']} ({stats['with_stock']/stats['total']*100:.1f}%)")
print(f"   Con imagen: {stats['with_image']} ({stats['with_image']/stats['total']*100:.1f}%)")
print("="*80)

conn.close()
