# Guía de API - Endpoints de Tiendas

## URLs Base

API Principal: `http://localhost:8000`

## Endpoints por Tienda

### 1. SercoPlus

**URL**: `/api/stores/sercoplus/products`

**Método**: GET

**Parámetros**:
- `skip` (opcional): Saltar N registros (default: 0)
- `limit` (opcional): Límite de resultados (default: 50)
- `component_type` (opcional): Filtrar por tipo de componente
- `brand` (opcional): Filtrar por marca

**Tipos de componentes válidos**:
- `placas-madre`
- `procesadores`
- `memorias-ram`
- `almacenamiento`
- `tarjetas-video`

**Ejemplo de respuesta**:
```json
{
  "store": "sercoplus",
  "total": 351,
  "skip": 0,
  "limit": 50,
  "count": 50,
  "products": [
    {
      "id": 1,
      "name": "PROCESADOR AMD RYZEN 5 5600XT",
      "component_type": "procesadores",
      "brand": "AMD",
      "sku": "110269018",
      "price_usd": 199.99,
      "price_local": 695.97,
      "currency": "PEN",
      "stock": "0",
      "store": "sercoplus",
      "source_url": "https://sercoplus.com/...",
      "image_url": "https://sercoplus.com/..."
    }
  ]
}
```

**Ejemplos de uso**:
```bash
# Todos los productos
curl "http://localhost:8000/api/stores/sercoplus/products"

# Solo procesadores
curl "http://localhost:8000/api/stores/sercoplus/products?component_type=procesadores"

# Procesadores AMD
curl "http://localhost:8000/api/stores/sercoplus/products?component_type=procesadores&brand=AMD"

# Paginación
curl "http://localhost:8000/api/stores/sercoplus/products?skip=50&limit=25"
```

---

### 2. PCImpacto

**URL**: `/api/stores/pcimpacto/products`

**Método**: GET

**Parámetros**: (iguales que SercoPlus)

**Tipos de componentes válidos**:
- `placas-madre`
- `procesadores`
- `memorias-ram`
- `almacenamiento`
- `tarjetas-video`

**Ejemplos de uso**:
```bash
# Todos los productos
curl "http://localhost:8000/api/stores/pcimpacto/products"

# Tarjetas de video
curl "http://localhost:8000/api/stores/pcimpacto/products?component_type=tarjetas-video"

# Memorias RAM Corsair
curl "http://localhost:8000/api/stores/pcimpacto/products?component_type=memorias-ram&brand=Corsair"
```

---

### 3. MemoryKings

**URL**: `/api/stores/memorykings/products`

**Método**: GET

**Parámetros**: (iguales que SercoPlus)

**Ejemplos de uso**:
```bash
# Todos los productos
curl "http://localhost:8000/api/stores/memorykings/products"

# Almacenamiento
curl "http://localhost:8000/api/stores/memorykings/products?component_type=almacenamiento"
```

---

## Endpoint de Comparación

### Comparar precios entre todas las tiendas

**URL**: `/api/stores/compare-all`

**Método**: GET

**Parámetros**:
- `component_type` (opcional): Filtrar por tipo
- `brand` (opcional): Filtrar por marca

**Respuesta**: Lista de productos con indicador de tienda más barata

```bash
# Comparar todos los procesadores
curl "http://localhost:8000/api/stores/compare-all?component_type=procesadores"
```

---

## Filtros Disponibles

### Marcas comunes:
- `AMD`
- `Intel`
- `NVIDIA`
- `Kingston`
- `Corsair`
- `Western Digital`
- `Samsung`
- `Crucial`
- `ASUS`
- `MSI`
- `Gigabyte`

### Component Types:
1. **placas-madre**: Placas madre / Motherboards
2. **procesadores**: CPUs / Procesadores
3. **memorias-ram**: Módulos de memoria RAM
4. **almacenamiento**: SSDs, HDDs, NVMe
5. **tarjetas-video**: Tarjetas gráficas / GPUs

---

## Códigos de Estado

- `200 OK`: Solicitud exitosa
- `404 Not Found`: Tienda no encontrada
- `500 Internal Server Error`: Error del servidor

---

## Notas

1. Todos los endpoints retornan JSON
2. Los nombres de tienda en la BD son minúsculas: `sercoplus`, `pcimpacto`, `memorykings`
3. Los component_type usan guiones: `placas-madre`, `tarjetas-video`
4. Los precios están en USD y PEN (soles peruanos)
5. La paginación por defecto es 50 productos por página
