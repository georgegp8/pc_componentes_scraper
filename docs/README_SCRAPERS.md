# 🛒 PC Price Scraper - Sistema Multi-Tienda

Sistema de scraping para comparación de precios de componentes de PC en tiendas peruanas.

## 📁 Estructura del Proyecto

```
pc_price_scraper/
├── scrapers/                    # Scrapers organizados por tienda
│   ├── memorykings/            # Scraper de MemoryKings
│   │   ├── __init__.py
│   │   ├── scraper.py          # Clase principal del scraper
│   │   ├── run.py              # Script para ejecutar scraping
│   │   ├── products.json       # Productos scrapeados
│   │   └── README.md           # Documentación específica
│   │
│   └── sercoplus/              # Scraper de SercoPlus
│       ├── __init__.py
│       ├── scraper.py          # Clase principal del scraper
│       ├── run.py              # Script para ejecutar scraping
│       └── products.json       # Productos scrapeados
│
├── database.py                 # Gestión de base de datos SQLite
├── main.py                     # API FastAPI para consultas
├── run_all_scrapers.py         # Script unificado para todas las tiendas
├── scraping_summary.json       # Resumen del último scraping
└── requirements.txt            # Dependencias del proyecto
```

## 🏪 Tiendas Implementadas

### 1. **MemoryKings** (325 productos)
- **Método:** Requests + BeautifulSoup (sin Selenium)
- **Categorías:** 4 (procesadores, tarjetas-video, memorias-ram, almacenamiento)
- **Procesadores:** 69 productos
  - Intel Core i3/i5/i7/i9/Ultra: 36 procesadores
  - AMD Ryzen 3000-9000 Series: 29 procesadores
- **Tarjetas de Video:** 75 productos (NVIDIA RTX 5000, AMD Radeon, Intel Arc)
- **Memorias RAM:** 55 productos (DDR3/DDR4/DDR5)
- **Almacenamiento:** 126 productos (SSD M.2 PCIe Gen3/4/5, HDD)
- **Calidad:** 100% de datos (precios, imágenes, stock)

### 2. **SercoPlus** (383 productos)
- **Método:** Selenium + ChromeDriver
- **Categorías:** 7 (procesadores, tarjetas-video, memorias-ram, ssd-m2, ssd-sata, hdd, placas-madre)
- **Calidad:** 99.6% imágenes, 100% precios y stock

## 🚀 Uso Rápido

### Ejecutar Scraper Individual

**MemoryKings:**
```bash
cd scrapers/memorykings
python run.py
```

**SercoPlus:**
```bash
cd scrapers/sercoplus
python run.py
```

### Ejecutar Todos los Scrapers

```bash
python run_all_scrapers.py
```

Esto ejecutará todos los scrapers y generará:
- `scrapers/memorykings/products.json` - Productos de MemoryKings
- `scrapers/sercoplus/products.json` - Productos de SercoPlus
- `scraping_summary.json` - Resumen general

## 📊 Datos Extraídos

Cada producto incluye:
```json
{
  "name": "Procesador Intel Core i5-14400",
  "normalized_name": "procesador intel core i5 14400",
  "component_type": "procesadores",
  "brand": "Intel",
  "sku": "026378",
  "price_usd": 205.0,
  "price_local": 705.0,
  "currency": "PEN",
  "stock": "10+",
  "store": "memorykings",
  "source_url": "https://www.memorykings.pe/producto/...",
  "image_url": "https://cdn.memorykings.pe/...",
  "category": "Procesadores Intel Core 14ᵃ Gen"
}
```

## 🎯 Categorías Alineadas

Ambas tiendas tienen categorías comparables:

| Categoría          | MemoryKings | SercoPlus |
|-------------------|-------------|-----------|
| Procesadores      | ✅ 69       | ✅ 73     |
| Tarjetas de Video | ✅ 75       | ✅ 29     |
| Memorias RAM      | ✅ 55       | ✅ 50     |
| Almacenamiento    | ✅ 126      | ✅ 231    |
| **TOTAL**         | **325**     | **383**   |

## 🔧 Configuración

### Requisitos
```bash
pip install -r requirements.txt
```

### Variables de Entorno (Opcional)
```bash
# Para rate limiting personalizado
SCRAPER_DELAY=0.5
MAX_PRODUCTS_PER_LISTADO=30
```

## 📝 Agregar Nueva Tienda

1. Crear carpeta en `scrapers/nombre_tienda/`
2. Crear `scraper.py` con clase del scraper
3. Crear `run.py` para ejecución
4. Agregar a `run_all_scrapers.py`

Ejemplo de estructura mínima:
```python
# scrapers/nueva_tienda/scraper.py
class NuevaTiendaScraper:
    def __init__(self):
        self.base_url = "https://nuevatienda.pe"
        self.categories = {...}
    
    def scrape_category(self, category_key):
        # Implementar lógica de scraping
        return products
```

## 🐛 Debugging

Para activar modo verbose:
```bash
DEBUG=1 python run_all_scrapers.py
```

## 📈 Próximos Pasos

- [ ] Agregar PCImpacto
- [ ] Integración con base de datos
- [ ] API REST para consultas
- [ ] Sistema de notificaciones de cambios de precio
- [ ] Dashboard web para visualización

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu rama de feature (`git checkout -b feature/nueva-tienda`)
3. Commit tus cambios (`git commit -am 'Agregar nueva tienda'`)
4. Push a la rama (`git push origin feature/nueva-tienda`)
5. Abre un Pull Request

## 📄 Licencia

MIT License - Ver LICENSE para más detalles

## 👤 Autor

Proyecto de comparación de precios de componentes de PC en Perú
