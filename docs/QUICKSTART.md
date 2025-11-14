# 🚀 Guía de Inicio Rápido

## Instalación en 3 pasos

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Iniciar el servidor
```bash
python main.py
```

### 3. Abrir el dashboard
Abre en tu navegador: `dashboard.html`

## URLs importantes

- **API**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs
- **Dashboard**: Abre `dashboard.html` en tu navegador

## Primer uso

### Desde el Dashboard (más fácil)
1. Abre `dashboard.html` en tu navegador
2. En la sección "Scrapear Tienda":
   - URL: `https://sercoplus.com/765-cpu-1700-12va-generacion`
   - Tienda: `SercoPlus`
3. Haz clic en "🚀 Iniciar Scraping"
4. Explora las otras secciones para buscar y comparar

### Desde la API directamente

**Scrapear productos:**
```bash
curl -X POST "http://localhost:8000/api/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://sercoplus.com/765-cpu-1700-12va-generacion",
    "store_name": "SercoPlus"
  }'
```

**Ver productos:**
```bash
curl "http://localhost:8000/api/products?limit=5"
```

**Buscar:**
```bash
curl "http://localhost:8000/api/search?query=Intel%20Core%20i7"
```

**Comparar precios:**
```bash
curl "http://localhost:8000/api/compare/PROCESADOR%20INTEL%20CORE%20I7-12700F"
```

## Con Docker

```bash
docker-compose up -d
```

## Ejecutar tests

```bash
python test_api.py
```

## Solución de problemas

### El servidor no inicia
- Verifica que el puerto 8000 esté libre
- Asegúrate de tener Python 3.8+

### No se encuentran productos
- Verifica que la URL sea correcta
- Algunos sitios pueden bloquear scrapers
- Revisa los logs para ver errores específicos

### Error de CORS en el dashboard
- Asegúrate de que el servidor esté corriendo
- Verifica que la URL de la API sea correcta

## Próximos pasos

1. **Scrapea más tiendas** para comparar precios
2. **Explora los filtros** por tipo de componente, marca, precio
3. **Usa la comparación** para encontrar las mejores ofertas
4. **Revisa las estadísticas** para análisis de mercado

## Soporte

- Documentación completa: `README.md`
- API docs: http://localhost:8000/docs
- Issues: GitHub

¡Feliz scraping! 🎉
