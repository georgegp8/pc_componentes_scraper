# 📊 Análisis de Rendimiento - PC Price Scraper

**Fecha:** 13 de Noviembre 2025  
**Versión:** 1.0

---

## 🔍 Análisis de MemoryKings

### ⏱️ Tiempos de Scraping (Estimados)

#### Configuración Actual (run.py):
- **MAX_LISTADOS:** 20 listados por categoría
- **MAX_PRODUCTS:** 30 productos por listado
- **Categorías:** 4 (procesadores, tarjetas-video, memorias-ram, almacenamiento)

#### Cálculo de Tiempo:

```
Tiempo por producto: 
  - Página de listado: 3s (wait_time)
  - Página de producto: 5s (wait_time) + 0.5s (sleep)
  - Total por producto: ~8.5s

Por categoría:
  - Productos esperados: 20 listados × 30 productos = 600 productos
  - Tiempo: 600 × 8.5s = 5,100s = 85 minutos
  - Con sleeps adicionales: ~90-95 minutos

Total (4 categorías):
  - Tiempo estimado: 4 × 90min = 360 minutos = 6 HORAS
```

### 🐌 Problemas Identificados

#### 1. **Selenium con Wait Times Largos**
```python
# scraper.py línea 90
soup = super().fetch_page(listado_url, wait_time=3)  # 3s por listado

# scraper.py línea 109
soup = super().fetch_page(product_url, wait_time=5)  # 5s por producto
```

**Impacto:** Cada producto requiere 5 segundos de espera aunque el contenido cargue en 1s.

#### 2. **Procesamiento Secuencial**
```python
# scraper.py líneas 318-328
for url in product_urls:
    product = self.scrape_product_page(url)
    if product:
        all_products.append(product)
    time.sleep(0.5)  # Rate limiting adicional
```

**Impacto:** Un producto a la vez, no hay paralelización.

#### 3. **Muchos Listados Configurados**
- **Procesadores:** 13 listados (Ryzen 3000, 4000, 5000, 7000, 8000, 9000, Intel 10ª, 12ª, 14ª, etc.)
- **Tarjetas de video:** 9 listados (RTX 5000 series, AMD RX, Intel Arc)
- **Memorias RAM:** 7 listados (DDR3, DDR4, DDR5 variants)
- **Almacenamiento:** 8 listados (SSD Gen3/4/5, HDD)

**Total:** 37 listados × 30 productos = 1,110 requests potenciales

#### 4. **Extracción Innecesaria de Datos**
```python
# scraper.py líneas 148-165
# Busca imagen en 3 métodos diferentes aunque og:image funcione
# Busca marca en logo aunque pueda extraerse del nombre
```

---

## ⚡ Optimizaciones Propuestas

### 1. **Reducir Wait Times (Ganancia: ~60%)**

```python
# Optimización: Esperar solo lo necesario
soup = super().fetch_page(listado_url, wait_time=1)  # 3s → 1s
soup = super().fetch_page(product_url, wait_time=2)  # 5s → 2s
```

**Impacto:** 8.5s/producto → 3.5s/producto = **~4 horas menos**

### 2. **Scraping Paralelo con ThreadPoolExecutor (Ganancia: ~70%)**

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def scrape_category_parallel(self, category_key, max_workers=5):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for url in product_urls:
            future = executor.submit(self.scrape_product_page, url)
            futures.append(future)
        
        for future in as_completed(futures):
            product = future.result()
            if product:
                all_products.append(product)
```

**Impacto:** 5 productos simultáneos = **1.2 horas total** (en vez de 6 horas)

### 3. **Scraping desde Listados (Ganancia: ~80%)**

En lugar de visitar cada página de producto, extraer datos directamente del listado:

```python
def scrape_category_quick(self, url):
    """Scraping rápido desde listado (como SercoPlus)"""
    soup = self.fetch_page(url)
    products = []
    
    for product_card in soup.find_all('div', class_='product-item'):
        # Extraer precio directamente
        price_elem = product_card.find('span', class_='price')
        # Extraer nombre
        name_elem = product_card.find('h2', class_='product-title')
        # Crear producto sin visitar página individual
        products.append(self.create_product_dict(...))
    
    return products
```

**Impacto:** Solo visita listados (37 páginas) = **~3-5 minutos total**

### 4. **Caché de Resultados**

```python
import hashlib
from pathlib import Path

def fetch_page_cached(self, url, cache_hours=24):
    cache_file = Path(f"cache/{hashlib.md5(url.encode()).hexdigest()}.html")
    
    if cache_file.exists():
        age = time.time() - cache_file.stat().st_mtime
        if age < cache_hours * 3600:
            return BeautifulSoup(cache_file.read_text(), 'html.parser')
    
    soup = self.fetch_page(url)
    cache_file.parent.mkdir(exist_ok=True)
    cache_file.write_text(str(soup))
    return soup
```

**Impacto:** Runs subsecuentes = **~0 segundos** (usa cache)

### 5. **Reducir Listados (Ganancia: ~50%)**

Enfocarse en listados con más productos:

```python
# Priorizar listados principales
priority_listados = {
    'procesadores': [
        'Ryzen 5000 Series',  # Más vendidos
        'Ryzen 7000 Series',  # Últimos
        'Intel Core 12ª Gen',
        'Intel Core 14ª Gen'
    ]
}
```

**Impacto:** 37 listados → 15 listados = **3 horas menos**

---

## 🏪 Comparación con SercoPlus

### SercoPlus (Más Rápido):
```python
# sercoplus_scraper.py línea 173
soup = self.fetch_page(page_url, wait_time=5)  # Solo para listados

# Extrae datos del listado directamente (líneas 183-221)
for container in product_containers:
    # No visita páginas individuales
    product = extract_from_card(container)
```

**Ventajas:**
- ✅ Solo visita páginas de listados (con paginación)
- ✅ Extrae precio, nombre, SKU del HTML del listado
- ✅ Maneja paginación automáticamente
- ✅ ~2-3 minutos por categoría

**Tiempo Total SercoPlus:** ~10-15 minutos para todas las categorías

### MemoryKings (Más Lento):
- ❌ Visita cada página de producto individualmente
- ❌ Wait time de 5s por producto
- ❌ Procesamiento secuencial
- ❌ ~90 minutos por categoría

**Tiempo Total MemoryKings:** ~6 horas para todas las categorías

---

## 🎯 Recomendaciones Inmediatas

### Opción 1: Quick Wins (Implementar YA) ⚡
1. **Reducir wait_times:** 5s → 2s (Ganancia: 3 horas)
2. **Reducir listados:** 37 → 20 prioritarios (Ganancia: 2 horas)
3. **Reducir productos por listado:** 30 → 15 (Ganancia: 1.5 horas)

**Resultado:** 6 horas → 1.5 horas (75% más rápido)

**Cambios en run.py:**
```python
MAX_LISTADOS = 10  # 20 → 10
MAX_PRODUCTS = 15  # 30 → 15
```

**Cambios en scraper.py:**
```python
soup = super().fetch_page(listado_url, wait_time=1)  # 3s → 1s
soup = super().fetch_page(product_url, wait_time=2)  # 5s → 2s
```

### Opción 2: Refactor Completo (Mejor a largo plazo) 🔨
1. **Implementar scraping paralelo** con ThreadPoolExecutor
2. **Scraping desde listados** como SercoPlus
3. **Caché de páginas** visitadas
4. **Detección inteligente de carga** (no wait times fijos)

**Resultado:** 6 horas → 5-10 minutos (98% más rápido)

---

## 🌐 Búsqueda de Páginas Similares a SercoPlus

### Características deseadas:
✅ Listados con precios visibles sin JavaScript  
✅ Paginación simple  
✅ Estructura HTML consistente  
✅ Datos completos en tarjetas de producto  
✅ Sin CAPTCHA o protecciones anti-bot  

### Tiendas Peruanas Recomendadas:

#### 1. **PC Factory** (https://www.pcfactory.cl - Perú)
- ✅ Listados claros con precios
- ✅ Paginación estándar
- ✅ Similar a SercoPlus
- ⚠️ Requiere verificar stock en Perú

#### 2. **Oechsle** (https://www.oechsle.pe - Tecnología)
- ✅ Tienda retail con sección PC
- ✅ HTML simple
- ⚠️ Catálogo limitado en componentes

#### 3. **Linio Perú** (https://www.linio.com.pe)
- ✅ Marketplace con múltiples vendedores
- ✅ Precios en soles
- ⚠️ Calidad variable de datos

#### 4. **Phantom** (https://www.phantomcomputers.com)
- ✅ Tienda especializada en gaming
- ✅ Catálogo completo
- ⚠️ Requiere análisis de estructura HTML

#### 5. **Xtreme PC** (https://xtremepc.com.pe)
- ✅ Especializado en componentes
- ✅ Precios competitivos
- ⚠️ Verificar estructura de listados

#### 6. **PC Gamer** (https://pcgamer.com.pe)
- ✅ Enfoque en gaming
- ✅ Stock local
- ⚠️ Analizar HTML primero

### Criterios de Selección:

**Prioridad Alta:**
1. Estructura HTML similar a SercoPlus
2. Precios visibles en listados (no requiere JS)
3. Sin CAPTCHA
4. Stock actualizado

**Prioridad Media:**
5. Catálogo de 500+ productos
6. Paginación funcional
7. Imágenes de calidad

**Bonus:**
8. API pública
9. Sitemap XML disponible
10. Datos estructurados (JSON-LD)

---

## 📝 Próximos Pasos

### Inmediato (Hoy):
1. ✅ Reducir MAX_LISTADOS y MAX_PRODUCTS en run.py
2. ✅ Reducir wait_times en scraper.py
3. ⏳ Ejecutar scraping optimizado de MemoryKings
4. ⏳ Medir tiempo real vs estimado

### Corto Plazo (Esta Semana):
1. ⏳ Investigar 2-3 tiendas de la lista recomendada
2. ⏳ Crear scrapers similares a SercoPlus
3. ⏳ Implementar scraping paralelo básico
4. ⏳ Agregar caché de páginas

### Mediano Plazo (Próximas 2 Semanas):
1. ⏳ Refactor completo de MemoryKings (estilo SercoPlus)
2. ⏳ Dashboard con comparación de tiendas
3. ⏳ Sistema de notificaciones de ofertas
4. ⏳ Histórico de precios

---

## 📊 Métricas de Éxito

| Métrica | Actual | Meta |
|---------|--------|------|
| Tiempo total | ~6 horas | ~15 minutos |
| Productos por hora | ~185 | ~4,000 |
| Wait time promedio | 5s | 1s |
| Éxito de extracción | ~85% | ~95% |
| Uso de CPU | Bajo (secuencial) | Medio (paralelo) |
| Cacheabilidad | 0% | 80% |

---

**Generado por:** GitHub Copilot  
**Última actualización:** 2025-11-13
