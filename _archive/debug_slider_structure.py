import requests
from bs4 import BeautifulSoup

url = "https://www.memorykings.pe/producto/350552/disco-duro-12tb-toshiba-n300-512mb-nas"

r = requests.get(url, timeout=10)
soup = BeautifulSoup(r.content, 'html.parser')

slider = soup.find('ul', id='slider-detalle')
if slider:
    print("Slider HTML completo:")
    print("="*80)
    print(slider.prettify()[:2000])
    print("="*80)
    
    print("\n\nTodos los <li> dentro del slider:")
    all_lis = slider.find_all('li')
    for i, li in enumerate(all_lis):
        classes = li.get('class', [])
        print(f"\n{i+1}. <li class='{' '.join(classes)}'>")
        img = li.find('img')
        if img:
            print(f"   IMG src: {img.get('src', 'NO SRC')[:100]}")
