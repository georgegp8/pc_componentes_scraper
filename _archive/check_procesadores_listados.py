"""
Verificar listados de procesadores en MemoryKings
"""
import requests
from bs4 import BeautifulSoup

url = 'https://www.memorykings.pe/subcategorias/26/procesadores'

response = requests.get(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

soup = BeautifulSoup(response.text, 'html.parser')

# Buscar todos los listados
links = soup.find_all('a', href=lambda x: x and '/listados/' in x)

print(f"📦 LISTADOS EN PROCESADORES ({len(links)} encontrados)")
print("="*70)

for i, link in enumerate(links, 1):
    href = link.get('href', '')
    title_elem = link.find('h4') or link.find('h3') or link.find('h5')
    name = title_elem.get_text(strip=True) if title_elem else link.get_text(strip=True)
    name = name.replace('»', '').strip()
    
    # Marcar si es procesador Intel o AMD
    tipo = ""
    if 'intel' in name.lower() and 'procesador' in name.lower():
        tipo = " ✅ INTEL"
    elif 'amd' in name.lower() and 'procesador' in name.lower():
        tipo = " ✅ AMD"
    elif 'athlon' in name.lower() or 'ryzen' in name.lower():
        tipo = " ✅ AMD"
    elif 'core' in name.lower() and 'laptop' not in name.lower():
        tipo = " ✅ INTEL"
    elif 'celeron' in name.lower() or 'pentium' in name.lower():
        tipo = " ⚠️ Intel Entry"
    
    print(f"{i:2}. {name}{tipo}")
    
print("\n" + "="*70)
