# 📱 PC Price Scraper API - Guía para Desarrolladores iOS

## 🎯 Overview

API REST optimizada para aplicaciones móviles que compara precios de componentes de PC entre las tres tiendas principales de Perú:
- **SercoPlus** (sercoplus.com)
- **MemoryKings** (memorykings.pe)  
- **PCImpacto** (impacto.com.pe)

### ✨ Características Principales

- 🤖 **Scraping Automático**: Actualización de precios cada 24 horas
- 🧠 **Matching Inteligente**: Detecta productos similares entre tiendas
- 📊 **Comparación de Precios**: Encuentra la mejor oferta automáticamente
- 📱 **Endpoints Optimizados para Móvil**: Respuestas ligeras y rápidas
- ⏰ **Tareas Programadas**: Sistema de actualización automática
- 📈 **Historial de Precios**: Tracking de cambios de precio

## 🚀 Inicio Rápido

### Instalación

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar environment
cp .env.example .env
# Edita .env según tus necesidades

# 3. Inicializar base de datos y tareas
python setup.py

# 4. Iniciar servidor
python main.py
```

El servidor estará en: `http://localhost:8000`

## 📱 Endpoints para iOS

### 1. Obtener Últimos Productos

```http
GET /api/mobile/latest?limit=20&component_type=procesador
```

**Respuesta:**
```json
{
  "count": 20,
  "products": [
    {
      "id": 1,
      "name": "PROCESADOR INTEL CORE I7-12700F",
      "brand": "Intel",
      "type": "procesador",
      "price_usd": 295.00,
      "price_pen": 1020.50,
      "stock": "high",
      "store": "SercoPlus",
      "url": "https://...",
      "updated": "2025-11-12T10:30:00"
    }
  ]
}
```

### 2. Mejores Ofertas

```http
GET /api/mobile/best-deals?component_type=procesador&limit=10
```

**Respuesta:**
```json
{
  "count": 10,
  "deals": [
    {
      "id": 5,
      "name": "Intel Core i5-12400F",
      "brand": "Intel",
      "price_usd": 130.40,
      "price_pen": 453.79,
      "store": "SercoPlus",
      "url": "https://...",
      "stores_available": 3
    }
  ]
}
```

### 3. Comparación Rápida

```http
GET /api/mobile/compare-quick/5
```

**Respuesta:**
```json
{
  "product": {
    "id": 5,
    "name": "Intel Core i5-12400F",
    "price_usd": 130.40,
    "store": "SercoPlus"
  },
  "alternatives": [
    {
      "id": 12,
      "name": "Procesador Intel Core i5 12400F",
      "price_usd": 131.00,
      "price_diff": 0.60,
      "store": "PCImpacto",
      "url": "https://...",
      "confidence": 95.5
    }
  ]
}
```

### 4. Buscar Productos

```http
GET /api/search?query=i7-12700&limit=20
```

### 5. Comparar Precios

```http
GET /api/compare/Intel%20Core%20i7-12700F?component_type=procesador
```

**Respuesta:**
```json
{
  "product_name": "Intel Core i7-12700F",
  "total_stores": 3,
  "matches": [...],
  "lowest_price": {
    "store": "SercoPlus",
    "price_usd": 295.00,
    "price_local": 1020.50,
    "url": "https://...",
    "stock": "high"
  },
  "highest_price": {
    "store": "MemoryKings",
    "price_usd": 310.00,
    "price_local": 1072.00
  },
  "price_difference_usd": 15.00,
  "savings_percentage": 4.84
}
```

### 6. Health Check

```http
GET /api/health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-12T10:30:00",
  "scheduler_running": true,
  "database": "connected"
}
```

## 🔧 Endpoints Administrativos

### Agregar Tarea Programada

```http
POST /api/schedule/add?store_name=SercoPlus&url=https://...&category=Procesadores&frequency_hours=24
```

### Ver Estado del Scheduler

```http
GET /api/schedule/status
```

### Ver Logs de Scraping

```http
GET /api/schedule/logs?limit=50&store_name=SercoPlus
```

### Ejecutar Scraping Manual

```http
POST /api/scrape
Content-Type: application/json

{
  "url": "https://sercoplus.com/765-cpu-1700-12va-generacion",
  "store_name": "SercoPlus"
}
```

## 📊 Tipos de Componentes

- `procesador` - CPUs (Intel, AMD)
- `tarjeta_grafica` - GPUs (NVIDIA, AMD)
- `memoria_ram` - Memoria RAM
- `almacenamiento` - SSDs, HDDs, NVMe
- `placa_madre` - Motherboards
- `fuente` - Fuentes de poder
- `gabinete` - Cases
- `refrigeracion` - Coolers
- `monitor` - Monitores
- `teclado` - Teclados
- `mouse` - Mouse
- `auriculares` - Headsets

## 🍎 Integración iOS (Swift)

### Modelo de Datos

```swift
struct Product: Codable {
    let id: Int
    let name: String
    let brand: String
    let type: String
    let priceUsd: Double
    let pricePen: Double?
    let stock: String
    let store: String
    let url: String?
    let updated: String?
    
    enum CodingKeys: String, CodingKey {
        case id, name, brand, type, stock, store, url, updated
        case priceUsd = "price_usd"
        case pricePen = "price_pen"
    }
}

struct ProductResponse: Codable {
    let count: Int
    let products: [Product]
}

struct Comparison: Codable {
    let productName: String
    let totalStores: Int
    let lowestPrice: PriceInfo
    let highestPrice: PriceInfo
    let priceDifferenceUsd: Double
    let savingsPercentage: Double
    
    enum CodingKeys: String, CodingKey {
        case totalStores = "total_stores"
        case lowestPrice = "lowest_price"
        case highestPrice = "highest_price"
        case productName = "product_name"
        case priceDifferenceUsd = "price_difference_usd"
        case savingsPercentage = "savings_percentage"
    }
}

struct PriceInfo: Codable {
    let store: String
    let priceUsd: Double
    let priceLocal: Double?
    let url: String?
    let stock: String?
    
    enum CodingKeys: String, CodingKey {
        case store, url, stock
        case priceUsd = "price_usd"
        case priceLocal = "price_local"
    }
}
```

### API Service

```swift
class PCPriceAPI {
    static let shared = PCPriceAPI()
    private let baseURL = "http://localhost:8000/api"
    
    func getLatestProducts(
        limit: Int = 20,
        componentType: String? = nil,
        completion: @escaping (Result<ProductResponse, Error>) -> Void
    ) {
        var components = URLComponents(string: "\(baseURL)/mobile/latest")!
        components.queryItems = [
            URLQueryItem(name: "limit", value: "\(limit)")
        ]
        
        if let type = componentType {
            components.queryItems?.append(
                URLQueryItem(name: "component_type", value: type)
            )
        }
        
        URLSession.shared.dataTask(with: components.url!) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(NSError(domain: "No data", code: -1)))
                return
            }
            
            do {
                let result = try JSONDecoder().decode(ProductResponse.self, from: data)
                completion(.success(result))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
    
    func compareProduct(
        name: String,
        completion: @escaping (Result<Comparison, Error>) -> Void
    ) {
        let encodedName = name.addingPercentEncoding(withAllowedCharacters: .urlPathAllowed)!
        let url = URL(string: "\(baseURL)/compare/\(encodedName)")!
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(NSError(domain: "No data", code: -1)))
                return
            }
            
            do {
                let result = try JSONDecoder().decode(Comparison.self, from: data)
                completion(.success(result))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
}
```

### Uso en ViewController

```swift
class ProductListViewController: UIViewController {
    
    override func viewDidLoad() {
        super.viewDidLoad()
        loadLatestProducts()
    }
    
    func loadLatestProducts() {
        PCPriceAPI.shared.getLatestProducts(limit: 20, componentType: "procesador") { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let response):
                    print("Loaded \(response.count) products")
                    // Update UI with response.products
                    
                case .failure(let error):
                    print("Error: \(error)")
                }
            }
        }
    }
    
    func compareProduct(name: String) {
        PCPriceAPI.shared.compareProduct(name: name) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let comparison):
                    let savings = comparison.savingsPercentage
                    print("Ahorra \(savings)% comprando en \(comparison.lowestPrice.store)")
                    
                case .failure(let error):
                    print("Error: \(error)")
                }
            }
        }
    }
}
```

## ⚙️ Configuración

### Variables de Entorno (.env)

```bash
# Base de datos
DATABASE_PATH=pc_prices.db

# API
API_HOST=0.0.0.0
API_PORT=8000

# Scraping
DEFAULT_SCRAPE_FREQUENCY_HOURS=24
SIMILARITY_THRESHOLD=0.75

# Scheduler
ENABLE_AUTO_SCRAPING=True
```

## 🐳 Docker

```bash
# Build y run con Docker Compose
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

## 📝 Características Avanzadas

### Actualización Automática

El sistema automáticamente actualiza los precios cada 24 horas. Las tareas se configuran en `setup.py`.

### Matching Inteligente

El sistema detecta productos similares entre tiendas usando:
- Normalización de nombres
- Extracción de números de modelo
- Comparación fuzzy
- Matching de SKUs

### Historial de Precios

Cada cambio de precio se registra en `price_history` table. Útil para:
- Gráficas de tendencia
- Alertas de bajada de precio
- Análisis histórico

## 🔒 Seguridad

- Rate limiting implementado (configurar en producción)
- CORS configurado (ajustar orígenes permitidos)
- No exponer en producción sin autenticación

## 📚 Documentación Completa

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Soporte

Para preguntas o issues, consulta el código fuente o documentación adicional.

## 📄 Licencia

MIT License - Ver archivo LICENSE
