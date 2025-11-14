"""
Test para verificar la extracción correcta de imágenes, stock y otros datos
"""
import sys
sys.path.insert(0, 'scrapers/memorykings')

from scraper import MemoryKingsScraper

# URL de prueba (del HTML que compartiste)
test_url = "https://www.memorykings.pe/producto/350552/disco-duro-12tb-toshiba-n300-512mb-nas"

print("="*80)
print("🧪 TEST: Extracción de Datos de Producto")
print("="*80)
print(f"\nURL: {test_url}\n")

scraper = MemoryKingsScraper()
product = scraper.scrape_product_page(test_url, component_type='almacenamiento')

if product:
    print("✅ PRODUCTO EXTRAÍDO CORRECTAMENTE\n")
    print(f"📝 Nombre: {product['name']}")
    print(f"💲 Precio USD: ${product['price_usd']}")
    print(f"💲 Precio PEN: S/{product['price_local']}")
    print(f"📦 Stock: {product['stock']}")
    print(f"🏷️ SKU: {product['sku']}")
    print(f"🏢 Marca: {product['brand']}")
    if product.get('image_url'):
        print(f"🖼️ Imagen: {product['image_url'][:80]}...")
    else:
        print(f"🖼️ Imagen: ❌ NULL")
    print(f"🔗 URL: {product['source_url']}")
    print(f"\n{'='*80}")
    
    # Verificar que todos los campos importantes existan
    issues = []
    if not product.get('image_url'):
        issues.append("❌ Imagen no capturada")
    elif 'marca' in product['image_url'].lower() or 'logo' in product['image_url'].lower():
        issues.append("⚠️ Imagen parece ser logo/marca")
    
    if product.get('stock') == 'unknown':
        issues.append("❌ Stock no capturado")
    
    if not product.get('sku'):
        issues.append("⚠️ SKU no capturado")
    
    if not product.get('brand'):
        issues.append("⚠️ Marca no identificada")
    
    if not product.get('price_usd') or not product.get('price_local'):
        issues.append("❌ Precios incompletos")
    
    if issues:
        print("\n⚠️ PROBLEMAS ENCONTRADOS:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("\n✅ TODOS LOS CAMPOS CORRECTOS!")
else:
    print("❌ NO SE PUDO EXTRAER EL PRODUCTO")

print("="*80)
