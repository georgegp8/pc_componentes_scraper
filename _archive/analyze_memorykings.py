"""
Script para analizar la estructura de MemoryKings
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import json

# Configurar Selenium
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

# Cargar página de procesadores
print("📄 Cargando página de MemoryKings...")
driver.get('https://www.memorykings.pe/subcategorias/26/procesadores')
time.sleep(7)  # Dar más tiempo para cargar JavaScript

# Parsear HTML
soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()

# Buscar diferentes estructuras posibles
print("\n🔍 Buscando estructura de productos...\n")

# Intento 1: div.producto
productos = soup.find_all('div', class_='producto')
print(f"div.producto: {len(productos)} encontrados")

# Intento 2: article.producto
productos = soup.find_all('article', class_='producto')
print(f"article.producto: {len(productos)} encontrados")

# Intento 3: div con clase que contenga 'prod'
productos = soup.find_all('div', class_=lambda x: x and 'prod' in str(x).lower())
print(f"div con 'prod': {len(productos)} encontrados")

# Intento 4: article con cualquier clase
productos = soup.find_all('article')
print(f"article (cualquiera): {len(productos)} encontrados")

# Intento 5: Buscar por atributos data-*
productos = soup.find_all(attrs={'data-product': True})
print(f"[data-product]: {len(productos)} encontrados")

productos = soup.find_all(attrs={'data-id': True})
print(f"[data-id]: {len(productos)} encontrados")

# Intento 6: Buscar contenedores comunes
productos = soup.find_all('div', class_='card')
print(f"div.card: {len(productos)} encontrados")

productos = soup.find_all('div', class_='item')
print(f"div.item: {len(productos)} encontrados")

# Intento 7: Ver si hay un contenedor principal
main_container = soup.find('main') or soup.find('div', {'id': 'productos'}) or soup.find('div', class_='productos')
if main_container:
    print(f"\n✅ Contenedor principal encontrado")
    # Buscar hijos directos
    children = main_container.find_all(recursive=False)
    print(f"   Hijos directos: {len(children)}")
    if children:
        print(f"   Primer hijo: {children[0].name} - class: {children[0].get('class')}")

# Mostrar estructura del primer producto si encontramos algo
for attempt_name, attempt_results in [
    ("div.producto", soup.find_all('div', class_='producto')),
    ("article.producto", soup.find_all('article', class_='producto')),
    ("article", soup.find_all('article')),
    ("div.card", soup.find_all('div', class_='card')),
]:
    if attempt_results:
        print(f"\n\n{'='*70}")
        print(f"📦 ESTRUCTURA DE: {attempt_name}")
        print('='*70)
        print(attempt_results[0].prettify()[:2000])
        break

# Buscar scripts de datos JSON
print("\n\n🔍 Buscando datos JSON en scripts...")
scripts = soup.find_all('script')
for i, script in enumerate(scripts):
    if script.string and ('producto' in script.string.lower() or 'product' in script.string.lower()):
        print(f"\n--- Script {i+1} con 'producto' ---")
        print(script.string[:500])
        if len(script.string) > 500:
            print("...")

print("\n✅ Análisis completo")
