# 🎉 PC Price Scraper - Sistema Mejorado

## 📋 Resumen de Mejoras Implementadas

Tu proyecto ha sido completamente rediseñado y mejorado para crear un sistema profesional de comparación de precios con las siguientes mejoras:

## ✨ Nuevas Características

### 1. 🏪 Scrapers Específicos por Tienda

**Antes:** Un scraper genérico que intentaba funcionar con todas las tiendas
**Ahora:** Scrapers especializados para cada tienda:

- **`SercoPlusScraper`** - Optimizado para sercoplus.com
- **`MemoryKingsScraper`** - Optimizado para memorykings.pe  
- **`PCImpactoScraper`** - Optimizado para impacto.com.pe

Cada scraper entiende la estructura HTML específica de su tienda, extrayendo:
- Nombre del producto
- Precios (efectivo y con tarjeta)
- SKU / Número de parte / Código interno
- Stock
- Marca
- Tipo de componente

### 2. 🤖 Sistema de Actualización Automática

**Archivo:** `scheduler.py`

- ⏰ Tareas programadas para scraping automático cada 24h
- 📊 Logging detallado de cada ejecución
- ⚙️ Configuración flexible de frecuencia
- 🔄 Ejecución en segundo plano
- 📈 Tracking de estado y estadísticas

**Ejemplo de uso:**
```python
# Agregar tarea programada
POST /api/schedule/add
{
  "store_name": "SercoPlus",
  "url": "https://sercoplus.com/765-cpu-1700-12va-generacion",
  "category": "Procesadores Intel 1700",
  "frequency_hours": 24
}
```

### 3. 🧠 Matching Inteligente de Productos

**Archivo:** `product_matcher.py`

El sistema ahora puede detectar que estos son el MISMO producto:
- "PROCESADOR INTEL CORE I5-12400F" (SercoPlus)
- "Procesador Intel Core i5 12400F 2.5Ghz" (MemoryKings)
- "Procesador Intel Core I5 12400f 2.5ghz" (PCImpacto)

**Técnicas utilizadas:**
- Normalización de nombres
- Extracción de números de modelo (i5-12400F, Ryzen 5 5600X, RTX 3060, etc.)
- Comparación fuzzy con SequenceMatcher
- Matching de SKUs
- Boost de confianza para coincidencias exactas

**Confidence score:**
- 95%+ = Muy alta confianza (SKU match)
- 90%+ = Alta confianza (modelo match)
- 75%+ = Confianza media (nombre similar)

### 4. 📊 Base de Datos Mejorada

**Nuevas tablas:**

```sql
-- Productos con normalización
products (
  ...campos anteriores...
  normalized_name TEXT,  -- Nombre normalizado para matching
  source_url TEXT UNIQUE, -- URL única del producto
  is_active INTEGER,      -- Flag para productos activos
  metadata TEXT          -- JSON con info adicional
)

-- Historial de precios extendido
price_history (
  ...campos anteriores...
  stock TEXT  -- También trackea cambios de stock
)

-- Matches entre productos
product_matches (
  product_id_1 INTEGER,
  product_id_2 INTEGER,
  confidence REAL,
  match_method TEXT
)

-- Programación de scraping
scraping_schedule (
  store_name TEXT,
  url TEXT,
  frequency_hours INTEGER,
  last_run TIMESTAMP,
  next_run TIMESTAMP
)

-- Logs de ejecución
scraping_logs (
  store_name TEXT,
  products_found INTEGER,
  products_saved INTEGER,
  status TEXT,
  duration_seconds REAL
)
```

### 5. 📱 Endpoints Optimizados para Mobile (iOS)

**Nuevos endpoints ligeros y rápidos:**

1. **`GET /api/mobile/latest`** - Últimos productos actualizados
2. **`GET /api/mobile/best-deals`** - Mejores ofertas actuales
3. **`GET /api/mobile/compare-quick/{id}`** - Comparación rápida
4. **`GET /api/health`** - Health check

**Características:**
- Respuestas compactas (solo datos esenciales)
- Campos con nombres mobile-friendly
- Paginación eficiente
- Cache-friendly

### 6. ⚙️ Sistema de Configuración

**Archivo:** `config.py` + `.env`

Toda la configuración centralizada:
```env
DATABASE_PATH=pc_prices.db
API_HOST=0.0.0.0
API_PORT=8000
DEFAULT_SCRAPE_FREQUENCY_HOURS=24
SIMILARITY_THRESHOLD=0.75
ENABLE_AUTO_SCRAPING=True
```

### 7. 🧪 Testing Mejorado

**Archivo:** `test_scrapers.py`

Tests completos para:
- Cada scraper individualmente
- Sistema de matching
- Endpoints de API
- Endpoints móviles

### 8. 🚀 Setup Automatizado

**Archivo:** `setup.py`

Script que:
- Inicializa la base de datos
- Crea tablas necesarias
- Agrega tareas programadas
- Opción de scraping inicial

## 📁 Estructura de Archivos Nueva

```
pc_price_scraper/
├── scrapers/                    # 🆕 Package de scrapers
│   ├── __init__.py
│   ├── base_scraper.py         # Clase base abstracta
│   ├── sercoplus_scraper.py    # Scraper SercoPlus
│   ├── memorykings_scraper.py  # Scraper MemoryKings
│   └── pcimpacto_scraper.py    # Scraper PCImpacto
│
├── database.py                  # ✨ Mejorado
├── main.py                      # ✨ Mejorado con nuevos endpoints
├── config.py                    # 🆕 Gestión de configuración
├── product_matcher.py           # 🆕 Sistema de matching
├── scheduler.py                 # 🆕 Tareas programadas
│
├── setup.py                     # 🆕 Script de inicialización
├── test_scrapers.py             # 🆕 Tests completos
├── test_api.py                  # ✅ Existente
│
├── .env.example                 # 🆕 Template de configuración
├── requirements.txt             # ✨ Actualizado
│
├── MOBILE_API_GUIDE.md          # 🆕 Guía para iOS
├── QUICKSTART.md                # ✅ Existente
├── README.md                    # ✅ Existente
│
├── dashboard.html               # ✅ Existente
├── docker-compose.yml           # ✅ Existente
└── Dockerfile                   # ✅ Existente
```

## 🎯 Casos de Uso Resueltos

### ✅ Actualización Automática Diaria

**Antes:** Había que ejecutar manualmente el scraping todos los días
**Ahora:** 
```python
# Se ejecuta automáticamente cada 24h
# Configurado en setup.py o vía API
```

### ✅ Comparación entre Tiendas

**Antes:** Difícil comparar productos con nombres diferentes
**Ahora:**
```python
# Encuentra automáticamente productos similares
GET /api/compare/Intel i5-12400F
# Retorna: SercoPlus $130, MemoryKings $145, PCImpacto $131
# Ahorro: 10.3%
```

### ✅ Consumo desde iOS

**Antes:** Respuestas genéricas y pesadas
**Ahora:**
```swift
PCPriceAPI.shared.getLatestProducts(limit: 20) { result in
    // Respuesta optimizada y ligera
}
```

## 📊 Comparación Antes/Después

| Característica | Antes | Ahora |
|----------------|-------|-------|
| Scrapers | 1 genérico | 3 especializados |
| Actualización | Manual | Automática 24h |
| Matching | Por nombre exacto | Inteligente + fuzzy |
| Base de datos | Básica | Completa con historial |
| API móvil | No optimizada | Endpoints dedicados |
| Configuración | Hardcoded | Archivo .env |
| Tests | Básicos | Completos por store |
| Documentación | README | README + Mobile Guide |

## 🚀 Cómo Empezar

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar

```bash
cp .env.example .env
# Edita .env si es necesario
```

### 3. Inicializar

```bash
python setup.py
# Esto crea la BD y agrega tareas programadas
```

### 4. Ejecutar

```bash
python main.py
# API disponible en http://localhost:8000
```

### 5. Probar

```bash
# Tests de scrapers
python test_scrapers.py

# Tests de API (requiere servidor corriendo)
python test_api.py
```

## 📱 Para Desarrolladores iOS

1. Lee `MOBILE_API_GUIDE.md` para guía completa
2. Endpoints principales:
   - `/api/mobile/latest` - Productos recientes
   - `/api/mobile/best-deals` - Mejores ofertas
   - `/api/mobile/compare-quick/{id}` - Comparar
   - `/api/compare/{name}` - Comparación completa

3. Ejemplo Swift incluido en la documentación

## 🔄 Flujo de Trabajo Recomendado

1. **Configuración Inicial:**
   - Ejecuta `setup.py`
   - Agrega URLs adicionales si necesitas

2. **Desarrollo:**
   - El scheduler actualiza precios automáticamente
   - Consulta logs en `/api/schedule/logs`
   - Monitorea estado en `/api/schedule/status`

3. **Consumo desde iOS:**
   - Usa endpoints `/api/mobile/*`
   - Implementa cache local
   - Actualiza cada vez que abres la app

## 🎓 Conceptos Avanzados

### Product Matching Confidence

```python
# Ejemplo de matching:
Product 1: "PROCESADOR INTEL CORE I5-12400F"
Product 2: "Intel i5 12400F"

Análisis:
- Modelo detectado: "I5-12400F" en ambos ✓
- Marca: "INTEL" en ambos ✓
- Similarity: 0.92 (92%)
- Confidence: 95% (boosted por modelo match)
```

### Normalized Names

```python
Original: "PROCESADOR INTEL CORE I5-12400F 2.5GHZ LGA1700"
Normalized: "I5 12400F 2.5GHZ LGA1700"
# Usado para comparación eficiente
```

### Smart Scraping

```python
# Quick scrape: Solo info de listado (rápido)
products = scraper.scrape_category_quick(url)

# Full scrape: Visita cada producto (completo)
products = scraper.scrape_category_page(url)
```

## 🔍 Troubleshooting

### Problema: No se encuentran productos

**Solución:**
1. Verifica que la URL sea correcta
2. Revisa logs: `GET /api/schedule/logs`
3. Prueba el scraper directamente: `python test_scrapers.py`

### Problema: Matching no funciona bien

**Solución:**
1. Ajusta `SIMILARITY_THRESHOLD` en `.env`
2. Ejecuta batch matching: 
   ```python
   matcher.batch_match_products()
   ```

### Problema: Scheduler no ejecuta

**Solución:**
1. Verifica `ENABLE_AUTO_SCRAPING=True` en `.env`
2. Chequea estado: `GET /api/schedule/status`
3. Ejecuta manualmente: `POST /api/schedule/run-now`

## 📚 Recursos Adicionales

- **API Docs:** http://localhost:8000/docs
- **Mobile Guide:** `MOBILE_API_GUIDE.md`
- **Quick Start:** `QUICKSTART.md`
- **Dashboard:** `dashboard.html`

## 🎉 Conclusión

Tu sistema ahora es:
- ✅ **Profesional**: Arquitectura modular y escalable
- ✅ **Automático**: Actualización sin intervención manual
- ✅ **Inteligente**: Matching avanzado entre tiendas
- ✅ **Mobile-Ready**: Optimizado para iOS
- ✅ **Mantenible**: Código limpio y documentado
- ✅ **Testeable**: Suite completa de tests

¡Listo para producción! 🚀
