"""
Analizar estructura de página de producto de MemoryKings
"""
import requests
from bs4 import BeautifulSoup
import json

url = 'https://www.memorykings.pe/producto/325783/procesador-athlon-3000g-3-50ghz-4mb-2c-am4'

print(f"📄 Analizando: {url}\n")

response = requests.get(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

soup = BeautifulSoup(response.text, 'html.parser')

print("="*70)
print("🔍 BUSCANDO ELEMENTOS CLAVE")
print("="*70)

# Nombre del producto
nombre = soup.find('h1')
print(f"\n📝 Nombre:")
print(f"   {nombre.get_text(strip=True) if nombre else 'No encontrado'}")

# Precio
precios = soup.find_all(class_=lambda x: x and 'price' in str(x).lower())
print(f"\n💰 Precios encontrados: {len(precios)}")
for i, precio in enumerate(precios[:3], 1):
    print(f"   {i}. {precio.get_text(strip=True)}")

# Imagen
imagen = soup.find('img', class_=lambda x: x and ('product' in str(x).lower() or 'main' in str(x).lower()))
if not imagen:
    imagen = soup.find('img', src=lambda x: x and 'files' in x)
print(f"\n🖼️ Imagen:")
if imagen:
    print(f"   src: {imagen.get('src')}")
else:
    print("   No encontrada")

# Stock/Disponibilidad
stock_elem = soup.find(class_=lambda x: x and ('stock' in str(x).lower() or 'disponib' in str(x).lower()))
print(f"\n📦 Stock:")
if stock_elem:
    print(f"   {stock_elem.get_text(strip=True)}")
else:
    print("   No encontrado")

# SKU/Código
sku = soup.find(class_=lambda x: x and ('sku' in str(x).lower() or 'code' in str(x).lower() or 'codigo' in str(x).lower()))
print(f"\n🏷️ SKU/Código:")
if sku:
    print(f"   {sku.get_text(strip=True)}")
else:
    print("   No encontrado")

# Marca
marca = soup.find(class_=lambda x: x and 'marca' in str(x).lower())
if not marca:
    marca = soup.find('span', string=lambda x: x and 'marca' in str(x).lower())
print(f"\n🏢 Marca:")
if marca:
    print(f"   {marca.get_text(strip=True)}")
else:
    print("   No encontrada")

# Especificaciones técnicas
specs = soup.find_all(class_=lambda x: x and ('spec' in str(x).lower() or 'caracteristica' in str(x).lower()))
print(f"\n📋 Especificaciones encontradas: {len(specs)}")
for i, spec in enumerate(specs[:5], 1):
    print(f"   {i}. {spec.get_text(strip=True)[:80]}")

print("\n" + "="*70)
print("📦 ESTRUCTURA HTML PRINCIPAL")
print("="*70)

# Buscar el contenedor principal del producto
main_container = soup.find('main') or soup.find('div', class_=lambda x: x and 'product' in str(x).lower())
if main_container:
    print("\nContenedor principal encontrado:")
    print(main_container.prettify()[:2000])
    print("...")
else:
    print("\nNo se encontró contenedor principal específico")
    # Mostrar primeros divs con contenido
    divs = soup.find_all('div', class_=True, limit=10)
    for div in divs:
        classes = ' '.join(div.get('class', []))
        if any(word in classes.lower() for word in ['product', 'item', 'detail', 'info']):
            print(f"\nDiv con clase potencial: {classes}")
            print(div.prettify()[:500])
            print("...")
            break

print("\n✅ Análisis completo")
