"""
Analizar si MemoryKings carga productos via API/AJAX
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import json

# Configurar Selenium con interceptación de red
options = Options()
options.add_argument('--headless')
options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

driver = webdriver.Chrome(options=options)

print("📄 Cargando MemoryKings con monitoreo de red...")
driver.get('https://www.memorykings.pe/subcategorias/26/procesadores')

# Esperar carga
time.sleep(8)

# Intentar encontrar productos por diferentes selectores
print("\n🔍 Intentando selectores CSS...")

selectors = [
    "div.producto",
    "article.producto", 
    ".product-item",
    ".product-card",
    "[data-product-id]",
    ".item-producto",
    "div[class*='prod']",
    "div[class*='item']",
    "a[href*='/producto/']",
    "a[href*='/productos/']",
]

for selector in selectors:
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            print(f"✅ {selector}: {len(elements)} elementos")
            # Mostrar HTML del primero
            if len(elements) > 0:
                print(f"   Primer elemento HTML:")
                print(f"   {elements[0].get_attribute('outerHTML')[:300]}...")
        else:
            print(f"❌ {selector}: 0 elementos")
    except Exception as e:
        print(f"⚠️ {selector}: Error - {str(e)[:50]}")

# Obtener logs de red
print("\n\n📡 Analizando llamadas de red...")
logs = driver.get_log('performance')
api_calls = []

for log in logs:
    try:
        log_data = json.loads(log['message'])
        message = log_data.get('message', {})
        method = message.get('method', '')
        
        if 'Network.response' in method:
            params = message.get('params', {})
            response = params.get('response', {})
            url = response.get('url', '')
            
            # Buscar URLs que puedan ser de productos
            if any(keyword in url.lower() for keyword in ['producto', 'product', 'subcategoria', 'api', 'catalog', 'items']):
                if url not in api_calls:
                    api_calls.append(url)
                    print(f"   🔗 {url}")
    except:
        pass

# Ver el HTML completo de un área específica
print("\n\n📦 HTML del contenedor principal:")
try:
    main = driver.find_element(By.TAG_NAME, "main")
    print(main.get_attribute('innerHTML')[:1500])
except:
    print("No se encontró <main>")

# Buscar contenedor de productos
print("\n\n🔍 Buscando contenedores con ID/clase 'productos':")
containers = driver.find_elements(By.CSS_SELECTOR, "#productos, .productos, #catalogo, .catalogo, .grid, .lista-productos")
for container in containers:
    print(f"   Encontrado: {container.tag_name} - id={container.get_attribute('id')} - class={container.get_attribute('class')}")
    children = container.find_elements(By.XPATH, "./*")
    print(f"   Tiene {len(children)} hijos")

driver.quit()
print("\n✅ Análisis completo")
