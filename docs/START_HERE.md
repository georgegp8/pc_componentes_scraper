# ✅ PC Price Scraper - Setup Completo

## 🎉 ¡Felicitaciones!

Tu sistema de comparación de precios ha sido completamente mejorado y está listo para usar.

## 📦 Lo que se ha implementado

### ✨ Características Nuevas

1. **✅ Scrapers Específicos por Tienda**
   - `SercoPlus Scraper` - Optimizado para sercoplus.com
   - `MemoryKingsScraper` - Optimizado para memorykings.pe
   - `PCImpactoScraper` - Optimizado para impacto.com.pe

2. **✅ Sistema de Actualización Automática**
   - Tareas programadas cada 24 horas
   - Scheduler en segundo plano
   - Logs detallados de ejecución

3. **✅ Matching Inteligente**
   - Detecta productos similares entre tiendas
   - Normalización de nombres
   - Extracción de modelos (i5-12400F, Ryzen 5 5600X, etc.)
   - Scoring de confianza

4. **✅ Base de Datos Mejorada**
   - Nuevas tablas: matches, schedule, logs
   - Historial de precios extendido
   - Índices optimizados

5. **✅ Endpoints para Mobile (iOS)**
   - `/api/mobile/latest` - Últimos productos
   - `/api/mobile/best-deals` - Mejores ofertas  
   - `/api/mobile/compare-quick/{id}` - Comparación rápida

6. **✅ Sistema de Configuración**
   - Archivo `.env` para config
   - Variables configurables
   - Setup automatizado

## 📂 Estructura de Archivos

```
pc_price_scraper/
├── 🆕 scrapers/              # Scrapers específicos
│   ├── base_scraper.py
│   ├── sercoplus_scraper.py
│   ├── memorykings_scraper.py
│   └── pcimpacto_scraper.py
│
├── ✨ database.py            # DB mejorada
├── ✨ main.py               # API mejorada
├── 🆕 config.py             # Configuración
├── 🆕 product_matcher.py    # Matching IA
├── 🆕 scheduler.py          # Tareas automáticas
│
├── 🆕 setup.py              # Inicialización
├── 🆕 test_scrapers.py      # Tests completos
│
├── 🆕 .env.example          # Config template
├── 🆕 MOBILE_API_GUIDE.md   # Guía iOS
├── 🆕 IMPROVEMENTS.md       # Resumen mejoras
├── 🆕 COMMANDS.md           # Comandos útiles
│
└── 🆕 ios_example/          # Ejemplo Swift
    └── PCPriceAPI.swift
```

## 🚀 Próximos Pasos

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar

```bash
# Copiar template de configuración
cp .env.example .env

# Editar .env si necesitas cambiar algo
# Por defecto ya funciona con configuración estándar
```

### 3. Inicializar Sistema

```bash
python setup.py
```

Esto:
- ✅ Crea la base de datos
- ✅ Agrega índices
- ✅ Configura tareas programadas
- ⚠️ Opcional: Ejecuta scraping inicial

### 4. Iniciar Servidor

```bash
python main.py
```

El servidor estará en: **http://localhost:8000**

### 5. Probar

```bash
# Tests de scrapers
python test_scrapers.py

# Tests de API (en otra terminal)
python test_api.py
```

### 6. Ver Documentación

- **Swagger UI**: http://localhost:8000/docs
- **Dashboard**: Abre `dashboard.html` en tu navegador

## 📱 Para iOS

1. Abre `MOBILE_API_GUIDE.md` para guía completa
2. Copia `ios_example/PCPriceAPI.swift` a tu proyecto Xcode
3. Cambia `baseURL` según tu configuración:
   ```swift
   // Desarrollo (simulador)
   private let baseURL = "http://localhost:8000/api"
   
   // Dispositivo real
   private let baseURL = "http://192.168.1.XX:8000/api"
   ```

4. Usa la API:
   ```swift
   PCPriceAPI.shared.getLatestProducts { result in
       // ... maneja resultado
   }
   ```

## ✨ Ejemplos de Uso

### Scrapear una tienda

```bash
curl -X POST "http://localhost:8000/api/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://sercoplus.com/765-cpu-1700-12va-generacion",
    "store_name": "SercoPlus"
  }'
```

### Comparar precios

```bash
curl "http://localhost:8000/api/compare/Intel%20Core%20i7-12700F"
```

### Buscar producto

```bash
curl "http://localhost:8000/api/search?query=i5-12400"
```

### Ver mejores ofertas (móvil)

```bash
curl "http://localhost:8000/api/mobile/best-deals?limit=10"
```

## 📊 Cómo Funciona

### 1. Scraping Automático

```
┌─────────────────┐
│   Scheduler     │ ← Ejecuta cada 24h
│   (Background)  │
└────────┬────────┘
         │
         ├─→ SercoPlus Scraper ─→ Base de Datos
         ├─→ MemoryKings Scraper ─→ Base de Datos
         └─→ PCImpacto Scraper ─→ Base de Datos
```

### 2. Matching Inteligente

```
Producto A (SercoPlus): "PROCESADOR INTEL CORE I5-12400F"
Producto B (MemoryKings): "Procesador Intel Core i5 12400F"
                              ↓
                    ┌─────────────────┐
                    │ Product Matcher │
                    └─────────────────┘
                              ↓
                    Normalización:
                    "I5-12400F" = "I5-12400F" ✓
                              ↓
                    Confidence: 95%
                              ↓
                    ¡SON EL MISMO PRODUCTO!
```

### 3. API Móvil

```
iOS App ─→ /api/mobile/latest ─→ JSON optimizado
                                  {
                                    "count": 20,
                                    "products": [...]
                                  }
```

## 🎯 Casos de Uso

### 1. App iOS de Comparación de Precios

Tu app puede:
- ✅ Mostrar últimos productos
- ✅ Buscar componentes específicos
- ✅ Comparar precios entre tiendas
- ✅ Mostrar mejores ofertas
- ✅ Ver historial de precios
- ✅ Alertas de bajadas de precio

### 2. Dashboard Web

- ✅ Ya incluido: `dashboard.html`
- ✅ Interfaz visual para administradores
- ✅ Búsqueda, filtros, comparación

### 3. Bot de Telegram/WhatsApp

Puedes agregar:
```python
# Notificación cuando baje precio
if new_price < old_price:
    send_telegram_message(f"¡Bajó el precio de {product}!")
```

### 4. Análisis de Mercado

- ✅ Estadísticas por tienda
- ✅ Productos más baratos
- ✅ Tendencias de precios

## 🔧 Mantenimiento

### Ver Estado del Scheduler

```bash
curl "http://localhost:8000/api/schedule/status"
```

### Ver Logs Recientes

```bash
curl "http://localhost:8000/api/schedule/logs?limit=20"
```

### Ejecutar Scraping Manual

```bash
curl -X POST "http://localhost:8000/api/schedule/run-now"
```

### Health Check

```bash
curl "http://localhost:8000/api/health"
```

## 📚 Documentación Adicional

- 📱 **[MOBILE_API_GUIDE.md](MOBILE_API_GUIDE.md)** - Guía iOS completa
- 🚀 **[QUICKSTART.md](QUICKSTART.md)** - Inicio rápido
- 🎉 **[IMPROVEMENTS.md](IMPROVEMENTS.md)** - Todas las mejoras
- 💻 **[COMMANDS.md](COMMANDS.md)** - Comandos útiles
- 📖 **[README.md](README.md)** - Documentación principal

## ⚠️ Notas Importantes

### Para Producción

1. **Cambiar SECRET_KEY**:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Configurar CORS** en `main.py`:
   ```python
   allow_origins=["https://tu-dominio.com"]
   ```

3. **Usar HTTPS**
4. **Agregar Rate Limiting**
5. **Usar Gunicorn** en vez de `python main.py`

### Límites de Scraping

- ⏱️ Delay de 2 segundos entre requests (respeta servidores)
- 🕐 Frecuencia mínima recomendada: 12 horas
- 🤝 Sé respetuoso con los sitios web

### URLs Incluidas

Ya configuradas en `scheduler.py`:

**SercoPlus:**
- Procesadores Intel 1700
- Procesadores AMD
- Tarjetas gráficas

**MemoryKings y PCImpacto:**
- URLs predefinidas disponibles
- Agrega más según necesites

## 🎓 Tips Avanzados

### 1. Mejorar Matching

Si encuentras productos que no matchean bien:

```python
# Ajusta el threshold en .env
SIMILARITY_THRESHOLD=0.70  # Más permisivo
# o
SIMILARITY_THRESHOLD=0.85  # Más estricto
```

### 2. Scraping Selectivo

```python
# Solo procesadores
curl "http://localhost:8000/api/products?component_type=procesador"

# Solo Intel
curl "http://localhost:8000/api/products?brand=Intel"

# Rango de precio
curl "http://localhost:8000/api/products?min_price=200&max_price=400"
```

### 3. Cache en iOS

```swift
class ProductCache {
    static let shared = ProductCache()
    private var cache: [String: (date: Date, products: [Product])] = [:]
    private let cacheLifetime: TimeInterval = 300 // 5 minutos
    
    func get(key: String) -> [Product]? {
        guard let cached = cache[key],
              Date().timeIntervalSince(cached.date) < cacheLifetime else {
            return nil
        }
        return cached.products
    }
    
    func set(key: String, products: [Product]) {
        cache[key] = (Date(), products)
    }
}
```

## 🎉 ¡Todo Listo!

Tu sistema está completamente configurado y listo para:

- ✅ Scrapear automáticamente cada 24h
- ✅ Comparar precios entre 3 tiendas
- ✅ Detectar productos similares
- ✅ Servir datos a tu app iOS
- ✅ Proveer estadísticas y análisis

## 🤝 Siguiente Paso

**¿Qué quieres hacer ahora?**

1. 📱 **Desarrollar app iOS** → Lee `MOBILE_API_GUIDE.md`
2. 🧪 **Probar sistema** → Ejecuta `python test_scrapers.py`
3. 🚀 **Poner en producción** → Lee sección de Producción
4. 🎨 **Personalizar** → Edita scrapers o agrega nuevas tiendas
5. 📊 **Ver dashboard** → Abre `dashboard.html`

---

**¿Dudas o problemas?**
- Revisa `COMMANDS.md` para comandos útiles
- Consulta logs: `logs/scraper.log`
- Verifica API: http://localhost:8000/docs

**¡Feliz scraping! 🎉**
