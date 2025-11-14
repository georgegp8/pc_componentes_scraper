"""
Test de búsqueda en MemoryKings
"""
import requests
from bs4 import BeautifulSoup

# Probar búsqueda
url = 'https://www.memorykings.pe/buscar/procesador'
print(f"📄 Probando búsqueda: {url}")

response = requests.get(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

soup = BeautifulSoup(response.text, 'html.parser')

# Buscar productos
products = soup.find_all('a', href=lambda x: x and '/producto/' in x)
print(f"\n✅ Productos encontrados en búsqueda: {len(products)}")

for i, p in enumerate(products[:10], 1):
    href = p.get('href')
    text = p.get_text(strip=True)
    print(f"{i}. {href}")
    print(f"   {text[:100]}")
