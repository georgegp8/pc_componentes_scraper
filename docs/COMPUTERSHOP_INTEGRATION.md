# 🆕 ComputerShop Peru - Integración Completa

## ✅ Estado: Completamente Integrado

ComputerShop Peru (computershopperu.com) ha sido integrado exitosamente al sistema de scraping.

## 📦 Archivos Creados

```
scrapers/computershop/
├── __init__.py          # Módulo de exportación
├── scraper.py           # Scraper principal
├── run.py               # Script de ejecución
├── load_to_db.py        # Cargador a base de datos
└── README.md            # Documentación

scrapers/
└── computershop_scraper.py  # Wrapper para import desde main.py

tests/
└── test_computershop.py     # Test rápido
```

## 🚀 Uso Rápido

### 1. Test Rápido (1 página)

```bash
cd tests
python test_computershop.py
```

### 2. Scrapear Todas las Categorías

```bash
cd scrapers/computershop
python run.py
```

Esto scrapeará:
- Placas madre
- Procesadores
- Memorias RAM
- Almacenamiento
- Tarjetas de video

### 3. Cargar a Base de Datos

```bash
python load_to_db.py
```

### 4. Desde la API

```bash
# Scrapear desde API
curl -X POST "http://localhost:8000/api/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://computershopperu.com/categoria/39-procesadores",
    "store_name": "ComputerShop"
  }'

# Obtener productos de ComputerShop
curl "http://localhost:8000/api/stores/computershop/products"

# Filtrar por categoría
curl "http://localhost:8000/api/stores/computershop/products?component_type=procesadores"

# Ver estadísticas
curl "http://localhost:8000/api/stores/computershop/stats"
```

## 📊 Categorías Configuradas

```python
categories = {
    'placas-madre': 'https://computershopperu.com/categoria/32-placas-madre',
    'procesadores': 'https://computershopperu.com/categoria/39-procesadores',
    'memorias-ram': 'https://computershopperu.com/categoria/51-memorias-ram-pc',
    'almacenamiento': 'https://computershopperu.com/categoria/36-almacenamiento',
    'tarjetas-video': 'https://computershopperu.com/categoria/20-tarjeta-de-video',
}
```

## 🔍 Datos Extraídos

Cada producto incluye:

✅ **Nombre completo**
✅ **Precio USD** (formato: $26,00)
✅ **Precio PEN** (formato: S/ 89,70)
✅ **Stock** (formato estándar: +20, 5, 0, etc.)
✅ **Marca** (extraída del HTML)
✅ **SKU** (código único)
✅ **URL del producto**
✅ **URL de imagen**
✅ **Tipo de componente** (auto-detectado)

## ⚙️ Características Técnicas

### Tecnología del Sitio
- **CMS**: PrestaShop
- **JavaScript**: Sí (requiere Selenium)
- **Paginación**: Automática

### Scraper
- **Método**: Selenium + BeautifulSoup
- **Wait time**: 3 segundos para JS
- **Rate limiting**: 2 segundos entre páginas
- **Manejo de errores**: Robusto

### Formatos Especiales

**Precios**: 
```
"$&nbsp;26,00&nbsp;&nbsp;&nbsp;(S/&nbsp;89,70)"
→ price_usd: 26.0, price_local: 89.7
```

**Stock**:
```
"Stock: >20" → "+20"
"Stock: 5" → "5"
"Últimas unidades en stock" → "1-4"
```

**Marca**:
```html
<span class="stock-mini">Marca: LIAN LI</span>
→ brand: "LIAN LI"
```

## 🧪 Testing

### Test Unitario
```bash
cd scrapers/computershop
python scraper.py
```

### Test de Integración
```bash
python tests/test_computershop.py
```

### Verificar Resultados
```bash
# Ver productos scrapeados
cat scrapers/computershop/products.json | python -m json.tool

# Contar productos
python -c "import json; data=json.load(open('scrapers/computershop/products.json')); print(f'Total: {data[\"total_products\"]} productos')"
```

## 📈 Rendimiento Estimado

- **Velocidad**: ~10-15 productos/minuto
- **Tiempo total**: 15-25 minutos (todas las categorías)
- **Productos esperados**: 200-400 productos
- **Tasa de éxito**: >95%

## 🔄 Integración con Sistema Existente

### main.py
✅ Agregado a lista de scrapers
✅ Endpoint `/api/stores/computershop/products` creado
✅ Incluido en `/api/stores/compare-all`
✅ Estadísticas en `/api/stores/computershop/stats`

### README.md
✅ Agregado a lista de tiendas
✅ Documentado en endpoints
✅ Incluido en instrucciones de scraping

### scripts/run_all_scrapers_complete.py
✅ Incluido en script de scraping completo
✅ Auto-carga a base de datos

## 🎯 Próximos Pasos

1. **Ejecutar scraping inicial**:
   ```bash
   cd scrapers/computershop
   python run.py
   python load_to_db.py
   ```

2. **Verificar integración**:
   ```bash
   python main.py
   # En otro terminal:
   curl "http://localhost:8000/api/stores/computershop/products"
   ```

3. **Configurar scraping automático** (opcional):
   - Agregar a scheduler cuando se reactive
   - Configurar frecuencia (recomendado: 24h)

## 📝 Notas Importantes

### Respeto al Servidor
- ⏱️ Delay de 2 segundos entre páginas
- 🤝 User-Agent completo
- 📊 Scraping fuera de horas pico recomendado

### Manejo de Cambios
Si ComputerShop cambia su HTML:
1. Revisar estructura en `scrapers/computershop/README.md`
2. Ajustar selectores en `scraper.py`
3. Ejecutar test: `python tests/test_computershop.py`

### Troubleshooting

**Error de Selenium**:
```bash
pip install --upgrade selenium
```

**Productos sin precio**:
- Verificar formato de precio en el HTML
- Algunos productos pueden estar sin publicar precio

**Timeout**:
- Aumentar `wait_time` en `scraper.py`
- Verificar conexión a internet

## ✅ Checklist de Integración

- [x] Scraper creado (`scraper.py`)
- [x] Script de ejecución (`run.py`)
- [x] Loader a BD (`load_to_db.py`)
- [x] Wrapper para import (`computershop_scraper.py`)
- [x] Integrado en `main.py`
- [x] Agregado a `scrapers/__init__.py`
- [x] Endpoint API creado
- [x] Actualizado `README.md`
- [x] Test creado (`test_computershop.py`)
- [x] Script completo actualizado
- [x] Documentación completa

## 🎉 ¡Listo para Usar!

ComputerShop está completamente integrado y listo para scrapear.

```bash
# Inicio rápido
cd scrapers/computershop
python run.py && python load_to_db.py
```

---

**Última actualización**: 14 de Noviembre, 2025
