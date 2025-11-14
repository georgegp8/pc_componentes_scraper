import requests
from bs4 import BeautifulSoup
import time

# Filtros configurados
filters = [
    'Procesadores AMD Athlon',
    'Procesadores AMD Ryzen',
    'Procesadores Intel Celeron',
    'Procesadores Intel Core 10',
    'Procesadores Intel Core 12',
    'Procesadores Intel Core 14',
    'Procesadores Intel Core Ultra',
    'Procesadores Intel Pentium'
]

url = 'https://www.memorykings.pe/subcategorias/26/procesadores'

print("🔍 Testeando filtros de procesadores...")
print("="*70)

response = requests.get(url, timeout=10)
soup = BeautifulSoup(response.content, 'html.parser')

# Buscar todos los enlaces a /listados/
links = soup.find_all('a', href=lambda x: x and '/listados/' in x)

print(f"Total de listados encontrados: {len(links)}\n")

matched = []
not_matched = []

for link in links:
    href = link.get('href', '')
    if not href:
        continue
    
    title_elem = link.find('h4') or link.find('h3') or link.find('h5')
    name = title_elem.get_text(strip=True) if title_elem else link.get_text(strip=True)
    name = name.replace('»', '').strip()
    
    # Verificar si pasa el filtro
    name_lower = name.lower()
    filter_match = None
    for f in filters:
        if f.lower() in name_lower:
            filter_match = f
            break
    
    if filter_match:
        matched.append({'name': name, 'filter': filter_match})
    else:
        # Verificar si es un listado de procesadores real
        if any(x in name for x in ['Procesadores AMD', 'Procesadores Intel']):
            not_matched.append(name)

print("✅ LISTADOS QUE PASAN EL FILTRO:")
print("="*70)
for i, item in enumerate(matched, 1):
    print(f"{i:2}. {item['name']}")
    print(f"    ✓ Match: {item['filter']}")

print(f"\n❌ LISTADOS DE PROCESADORES QUE NO PASAN:")
print("="*70)
for i, name in enumerate(not_matched, 1):
    print(f"{i:2}. {name}")

print(f"\n📊 RESUMEN:")
print(f"   Listados filtrados: {len(matched)}")
print(f"   Listados perdidos: {len(not_matched)}")
