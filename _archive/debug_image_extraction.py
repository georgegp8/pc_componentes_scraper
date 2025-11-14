import requests
from bs4 import BeautifulSoup

url = "https://www.memorykings.pe/producto/350552/disco-duro-12tb-toshiba-n300-512mb-nas"

print("🔍 DEBUG: Extracción de imagen del slider\n")

r = requests.get(url, timeout=10)
soup = BeautifulSoup(r.content, 'html.parser')

# Buscar slider
slider = soup.find('ul', id='slider-detalle')
print(f"1. Slider encontrado: {slider is not None}")

if slider:
    slides = slider.find_all('li', class_='lslide')
    print(f"2. Slides con clase 'lslide': {len(slides)}")
    
    print("\n3. Analizando cada slide:")
    for i, slide in enumerate(slides):
        print(f"\n   Slide {i+1}:")
        img = slide.find('img')
        if img:
            src = img.get('src')
            print(f"   - src: {src}")
            print(f"   - Tiene 'cdn.memorykings.pe/files/': {'cdn.memorykings.pe/files/' in src if src else False}")
            print(f"   - Tiene 'MK': {'MK' in src if src else False}")
            print(f"   - Tiene '/files/': {'/files/' in src if src else False}")
        else:
            print(f"   - No tiene <img>")
    
    print("\n4. Probando lógica del scraper:")
    image_url = None
    
    # Primera pasada: buscar con 'MK'
    for slide in slides:
        img_elem = slide.find('img')
        if img_elem:
            src = img_elem.get('src')
            if src and 'cdn.memorykings.pe/files/' in src:
                if 'MK' in src:
                    image_url = src
                    print(f"   ✅ Encontrada con 'MK': {src[:80]}...")
                    break
    
    # Segunda pasada: cualquier imagen de /files/
    if not image_url:
        print("   ⚠️ No encontró con 'MK', intentando segunda pasada...")
        for slide in slides:
            img_elem = slide.find('img')
            if img_elem:
                src = img_elem.get('src')
                if src and '/files/' in src and any(ext in src.lower() for ext in ['.jpg', '.png', '.webp']):
                    if not any(x in src.lower() for x in ['cintillo', 'banner', 'slide', 'promo', 'envios']):
                        image_url = src
                        print(f"   ✅ Encontrada sin 'MK': {src[:80]}...")
                        break
    
    if not image_url:
        print("   ❌ NO SE ENCONTRÓ IMAGEN")
    
    print(f"\n5. Resultado final: {image_url}")
