# PC Price Scraper

Sistema de scraping y comparación de precios de componentes de PC de tiendas peruanas.

## 🏪 Tiendas Integradas

- **SercoPlus** (sercoplus.com)
- **PCImpacto** (impacto.com.pe)
- **CycComputer** (cyccomputer.pe)
- **ComputerShop** (computershopperu.com)

**Total aproximado: 1,000+ productos**

## 📦 Categorías Estándar

Todas las tiendas usan las mismas categorías:
- `placas-madre` - Placas madre / Motherboards
- `procesadores` - Procesadores / CPUs
- `memorias-ram` - Memoria RAM
- `almacenamiento` - Discos SSD/HDD
- `tarjetas-video` - Tarjetas gráficas / GPUs

## 🚀 Inicio Rápido

### 1. Instalar dependencias

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Ejecutar API

```bash
python main.py
```

La API estará disponible en: `http://localhost:8000`

### 3. Scrapear datos

```bash
# SercoPlus
cd scrapers/sercoplus
python run.py
cd ../..
python scripts/load_sercoplus_to_db.py

# PCImpacto
cd scrapers/impacto
python run.py
python load_to_db.py

# ComputerShop (Nueva tienda)
cd scrapers/computershop
python run.py
python load_to_db.py
```

## 📡 Endpoints API

### Tiendas Específicas

- **SercoPlus**: `GET /api/stores/sercoplus/products`
- **PCImpacto**: `GET /api/stores/pcimpacto/products`
- **CycComputer**: `GET /api/stores/cyccomputer/products`
- **ComputerShop**: `GET /api/stores/computershop/products`

### Parámetros de consulta

```
?component_type=procesadores    # Filtrar por categoría
?brand=AMD                       # Filtrar por marca
?skip=0&limit=50                # Paginación
```

### Ejemplos

```bash
# Todos los procesadores de SercoPlus
curl "http://localhost:8000/api/stores/sercoplus/products?component_type=procesadores"

# Tarjetas AMD de Impacto
curl "http://localhost:8000/api/stores/pcimpacto/products?component_type=tarjetas-video&brand=AMD"

# Comparar precios entre todas las tiendas
curl "http://localhost:8000/api/stores/compare-all"
```

## 📁 Estructura del Proyecto

```
pc_price_scraper/
├── main.py                 # API FastAPI
├── database.py            # Módulo de base de datos
├── pc_prices.db          # SQLite database
├── requirements.txt      # Dependencias Python
├── dashboard.html        # Dashboard web
│
├── scrapers/             # Scrapers por tienda
│   ├── base_scraper.py   # Clase base
│   ├── sercoplus/        # Scraper SercoPlus
│   │   ├── scraper.py
│   │   ├── run.py
│   │   └── products.json
│   ├── impacto/          # Scraper Impacto
│   │   ├── scraper.py
│   │   ├── run.py
│   │   ├── load_to_db.py
│   │   └── products.json
│   └── memorykings/      # Scraper MemoryKings
│
├── scripts/              # Scripts de utilidad
│   ├── load_sercoplus_to_db.py
│   ├── clean_database.py
│   └── run_all_scrapers.py
│
├── docs/                 # Documentación
│   ├── API_STORES_GUIDE.md
│   ├── ANALISIS_RENDIMIENTO.md
│   └── GUIA_LIMPIEZA_BD.md
│
└── tests/                # Tests
    └── test_store_endpoints.py
```

## 🛠️ Mantenimiento

### Limpiar base de datos

```bash
python scripts/clean_database.py --db pc_prices.db --execute
```

### Ver estadísticas

```bash
python scripts/clean_database.py --db pc_prices.db --stats-only
```

### Eliminar productos antiguos (más de 30 días)

```bash
python scripts/clean_database.py --db pc_prices.db --remove-old --days 30 --execute
```

## 📊 Base de Datos

**Esquema de productos:**

```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    normalized_name TEXT,
    component_type TEXT,           -- placas-madre, procesadores, etc.
    brand TEXT,
    sku TEXT,
    price_usd REAL NOT NULL,
    price_local REAL,
    currency TEXT,
    stock TEXT,
    store TEXT NOT NULL,           -- sercoplus, pcimpacto, memorykings
    source_url TEXT UNIQUE,
    image_url TEXT,
    last_scraped TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1,
    metadata TEXT
);
```

## 🔧 Configuración

- **Python**: 3.11+
- **Selenium**: WebDriver automático (ChromeDriver)
- **Base de datos**: SQLite
- **Framework API**: FastAPI

## 📖 Documentación Adicional

- [Guía de API de Tiendas](docs/API_STORES_GUIDE.md)
- [Análisis de Rendimiento](docs/ANALISIS_RENDIMIENTO.md)
- [Guía de Limpieza de BD](docs/GUIA_LIMPIEZA_BD.md)

## 🐳 Docker (Opcional)

```bash
docker-compose up -d
```

## 📝 Notas

- Los scrapers usan Selenium con ChromeDriver automático
- Tiempo estimado de scraping: 15-20 minutos por tienda
- La API incluye hot-reload para desarrollo
- Los nombres de categorías están estandarizados en todas las tiendas
