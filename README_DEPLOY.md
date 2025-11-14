# PC Price Scraper API

Sistema de web scraping para comparar precios de componentes de PC de tiendas peruanas.

## 🏪 Tiendas

- SercoPlus (sercoplus.com)
- PCImpacto (impacto.com.pe)
- CycComputer (cyccomputer.pe)
- ComputerShop (computershopperu.com)

## 🚀 Deploy en Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Pasos:

1. Fork este repositorio
2. Conecta tu cuenta de Render con GitHub
3. Crea un nuevo Web Service
4. Selecciona este repositorio
5. Render detectará automáticamente `render.yaml`
6. Click en "Create Web Service"

## 📡 API Endpoints

### Productos por tienda
- `GET /api/stores/sercoplus/products`
- `GET /api/stores/pcimpacto/products`
- `GET /api/stores/cyccomputer/products`
- `GET /api/stores/computershop/products`

### Parámetros
```
?component_type=procesadores    # Filtrar por categoría
?brand=AMD                       # Filtrar por marca
?skip=0&limit=50                # Paginación
```

### Otros endpoints
- `GET /api/products` - Todos los productos
- `GET /api/stores/{store}/stats` - Estadísticas por tienda
- `GET /api/stores/compare-all` - Comparar todas las tiendas
- `GET /api/search?query=...` - Buscar productos
- `POST /api/scrape` - Scrapear una URL

## 🔧 Desarrollo Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor
python main.py

# API disponible en: http://localhost:8000
# Documentación: http://localhost:8000/docs
```

## 📦 Categorías

- `procesadores` - Procesadores / CPUs
- `tarjetas-video` - Tarjetas gráficas / GPUs
- `memorias-ram` - Memoria RAM
- `almacenamiento` - Discos SSD/HDD
- `placas-madre` - Placas madre / Motherboards

## 🐳 Docker

```bash
docker-compose up -d
```

## 📝 Licencia

MIT
