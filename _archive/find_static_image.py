import requests
from bs4 import BeautifulSoup

url = "https://www.memorykings.pe/producto/350552/disco-duro-12tb-toshiba-n300-512mb-nas"

r = requests.get(url, timeout=10)
soup = BeautifulSoup(r.content, 'html.parser')

print("🔍 Buscando imágenes en HTML estático:\n")

# Meta tags
print("1. Meta tags OG/Twitter:")
og_image = soup.find('meta', property='og:image')
if og_image:
    print(f"   og:image: {og_image.get('content')}")

twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
if twitter_image:
    print(f"   twitter:image: {twitter_image.get('content')}")

# Itemprop image
print("\n2. Itemprop image:")
itemprop_img = soup.find('meta', attrs={'itemprop': 'image'})
if itemprop_img:
    print(f"   itemprop=image: {itemprop_img.get('content')}")

# Link rel=image_src
print("\n3. Link rel=image_src:")
link_img = soup.find('link', rel='image_src')
if link_img:
    print(f"   image_src: {link_img.get('href')}")

# Cualquier img con id o clase que sugiera principal
print("\n4. Imágenes con clases/ids importantes:")
main_imgs = soup.find_all('img', attrs={'id': lambda x: x and 'main' in x.lower()})
for img in main_imgs[:3]:
    print(f"   - {img.get('id')}: {img.get('src', img.get('data-src'))}")

# Buscar noscript (a veces tienen la imagen fallback)
print("\n5. Imágenes dentro de <noscript>:")
noscripts = soup.find_all('noscript')
for ns in noscripts:
    imgs = ns.find_all('img')
    for img in imgs:
        src = img.get('src')
        if src and '/files/' in src:
            print(f"   - {src}")
