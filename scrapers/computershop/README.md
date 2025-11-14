# ComputerShop Peru Scraper

Scraper para **ComputerShop Peru** (computershopperu.com)

## 🏪 Tienda

- **Nombre**: ComputerShop Peru
- **URL**: https://computershopperu.com
- **Tecnología**: PrestaShop
- **Método**: Selenium (JavaScript rendering)

## 📦 Categorías

```python
categories = {
    'placas-madre': 'https://computershopperu.com/categoria/32-placas-madre',
    'procesadores': 'https://computershopperu.com/categoria/39-procesadores',
    'memorias-ram': 'https://computershopperu.com/categoria/51-memorias-ram-pc',
    'almacenamiento': 'https://computershopperu.com/categoria/36-almacenamiento',
    'tarjetas-video': 'https://computershopperu.com/categoria/20-tarjeta-de-video',
}
```

## 🚀 Uso

### 1. Scrapear todas las categorías

```bash
cd scrapers/computershop
python run.py
```

Esto generará un archivo `products.json` con todos los productos.

### 2. Cargar a la base de datos

```bash
python load_to_db.py
```

### 3. Test rápido

```bash
# Solo primera página de procesadores
python scraper.py
```

## 📊 Datos Extraídos

Cada producto incluye:

- ✅ **Nombre**: Nombre completo del producto
- ✅ **Precio USD**: Precio en dólares
- ✅ **Precio PEN**: Precio en soles
- ✅ **Stock**: Cantidad disponible (formato estándar)
- ✅ **Marca**: Extraída del HTML o nombre
- ✅ **SKU**: Código único del producto
- ✅ **URL**: Link al producto
- ✅ **Imagen**: URL de la imagen
- ✅ **Categoría**: Tipo de componente

## 🔍 Estructura HTML

ComputerShop usa PrestaShop con la siguiente estructura:

```html
<div class="product-container">
  <h5 class="product-name">
    <a href="[URL]">[NOMBRE]</a>
  </h5>
  
  <span class="product-price">
    $&nbsp;26,00&nbsp;&nbsp;&nbsp;(S/&nbsp;89,70)
  </span>
  
  <span class="stock-mini" data-stock="2">
    Stock: &gt;20
  </span>
  
  <span class="stock-mini">
    Marca: LIAN LI
  </span>
  
  <meta itemprop="sku" content="108400002">
</div>
```

## ⚙️ Características

### Manejo de Precios

- Formato: `$26,00 (S/ 89,70)`
- Extrae ambos: USD y PEN
- Normaliza formatos europeos (coma decimal)

### Manejo de Stock

- `Stock: >20` → `+20` (más de 20)
- `Stock: 5` → `5` (exacto)
- `Últimas unidades` → `1-4` (pocas unidades)
- Sin stock → `0`

### Paginación

- Detecta automáticamente páginas disponibles
- Extrae todos los productos sin límite
- Respeta delays entre requests (2 segundos)

## 📝 Notas Técnicas

1. **Selenium requerido**: La página usa JavaScript para cargar productos
2. **Wait time**: 3 segundos para carga de JS
3. **Headers**: User-Agent completo para evitar bloqueos
4. **Rate limiting**: 2 segundos entre páginas

## 🧪 Testing

```bash
# Test del scraper
python scraper.py

# Verificar resultados
cat products.json | grep -c "name"
```

## 📈 Rendimiento

- **Velocidad**: ~10-15 productos/minuto
- **Tiempo estimado**: 15-20 minutos para todas las categorías
- **Tasa de éxito**: >95% de productos con datos completos

## 🔧 Troubleshooting

### Selenium no inicia

```bash
# Actualizar ChromeDriver automático
pip install --upgrade selenium
```

### Productos sin precio

- Verificar formato en el HTML
- Algunos productos pueden no tener precio publicado

### Timeout errors

```bash
# Aumentar wait_time en scraper.py
soup = self.fetch_page(page_url, wait_time=5)  # Cambiar de 3 a 5
```

## 📊 Ejemplo de Producto

```json
{
  "name": "SOPORTE PARA TARJETA GRAFICA LIAN LI GB-002",
  "price_usd": 26.0,
  "price_local": 89.7,
  "currency": "PEN",
  "stock": "+20",
  "brand": "LIAN LI",
  "sku": "108400002",
  "component_type": "tarjetas-video",
  "store": "computershop",
  "source_url": "https://computershopperu.com/producto/...",
  "image_url": "https://computershopperu.com/6630-home_default/..."
}
```

## 🔄 Actualización

Para actualizar los datos:

```bash
# 1. Scrapear datos actualizados
python run.py

# 2. Cargar a base de datos (actualiza automáticamente)
python load_to_db.py
```

La base de datos detecta productos existentes por URL y actualiza precios/stock.
