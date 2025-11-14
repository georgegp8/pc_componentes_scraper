import requests
from bs4 import BeautifulSoup

print("🔍 Mapeando todas las categorías de SercoPlus...\n")

base_url = "https://sercoplus.com"

# Verificar categorías conocidas
categories_to_test = [
    (37, "procesadores"),
    (55, "memorias-ram"),
    (38, "tarjetas-video"),
    (39, "almacenamiento"),
    (40, "disco-duro"),
    (41, "ssd"),
    (42, "placa-madre"),
    (43, "fuente"),
]

found_categories = {}

for cat_id, name in categories_to_test:
    try:
        url = f"{base_url}/{cat_id}-{name}"
        r = requests.get(url, timeout=10, allow_redirects=True)
        
        if r.status_code == 200:
            soup = BeautifulSoup(r.content, 'html.parser')
            
            # Contar productos
            products = soup.find_all('article', class_='product-miniature') or \
                      soup.find_all('div', class_='product-container') or \
                      soup.find_all('div', class_='js-product')
            
            if products:
                found_categories[name] = {
                    'id': cat_id,
                    'url': url,
                    'products_found': len(products)
                }
                print(f"✅ {name.upper()}: {url}")
                print(f"   📦 ~{len(products)} productos encontrados en primera página")
            else:
                print(f"⚠️  {name}: {url} (sin productos visibles)")
        else:
            print(f"❌ {name}: Status {r.status_code}")
    
    except Exception as e:
        print(f"❌ {name}: Error - {str(e)[:50]}")

print(f"\n\n{'='*70}")
print(f"✅ CATEGORÍAS VÁLIDAS: {len(found_categories)}")
print('='*70)

for name, info in found_categories.items():
    print(f"\n'{name}': '{info['url']}',  # ~{info['products_found']} productos")
