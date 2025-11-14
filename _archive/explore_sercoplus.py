import requests
from bs4 import BeautifulSoup

print("🔍 Explorando SercoPlus...")

try:
    r = requests.get('https://www.sercoplus.com', timeout=10)
    print(f'Status: {r.status_code}')
    
    soup = BeautifulSoup(r.content, 'html.parser')
    
    # Buscar enlaces de categorías
    print("\n📦 Categorías encontradas:")
    links = soup.find_all('a', href=True)
    
    keywords = ['procesador', 'tarjeta', 'memoria', 'almacenamiento', 'disco', 'ssd', 'hdd', 'ram']
    
    found = []
    for link in links:
        text = link.get_text(strip=True).lower()
        href = link['href']
        
        for keyword in keywords:
            if keyword in text and href not in found:
                print(f"  {link.get_text(strip=True)}: {href}")
                found.append(href)
                break
    
    # Buscar en menú principal
    print("\n🔍 Buscando menú principal...")
    menu = soup.find('nav') or soup.find('ul', class_='menu')
    if menu:
        menu_links = menu.find_all('a', href=True)
        print(f"  Enlaces en menú: {len(menu_links)}")
        for link in menu_links[:15]:
            print(f"  - {link.get_text(strip=True)}: {link['href']}")
    
except Exception as e:
    print(f"❌ Error: {e}")
