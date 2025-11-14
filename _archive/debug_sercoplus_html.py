import requests
from bs4 import BeautifulSoup

url = "https://sercoplus.com/37-procesadores"

print(f"🔍 Analizando estructura HTML de: {url}\n")

r = requests.get(url, timeout=10)
soup = BeautifulSoup(r.content, 'html.parser')

print("="*70)
print("1. Buscando contenedores de productos:")
print("="*70)

# Probar diferentes selectores
selectors = [
    ('article.product-miniature', soup.find_all('article', class_='product-miniature')),
    ('div.product-container', soup.find_all('div', class_='product-container')),
    ('div.js-product', soup.find_all('div', class_='js-product')),
    ('div.product', soup.find_all('div', class_='product')),
    ('article', soup.find_all('article')),
]

for selector_name, elements in selectors:
    print(f"\n{selector_name}: {len(elements)} encontrados")
    if elements:
        print(f"   ✅ ENCONTRADO - Primer elemento:")
        print(f"   {str(elements[0])[:200]}...")

# Buscar cualquier artículo o div con "product" en la clase
print("\n" + "="*70)
print("2. Buscando tags con 'product' en clase:")
print("="*70)

all_divs = soup.find_all(['div', 'article'])
product_divs = [d for d in all_divs if d.get('class') and any('product' in c.lower() for c in d.get('class', []))]

print(f"\nEncontrados {len(product_divs)} elementos con 'product' en clase")
if product_divs:
    for i, div in enumerate(product_divs[:3]):
        classes = ' '.join(div.get('class', []))
        print(f"\n{i+1}. <{div.name} class='{classes}'>")
        print(f"   {str(div)[:300]}...")
