# Desplegar en Fly.io

## Instalación

```bash
# Instalar Fly CLI
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

## Despliegue

```bash
# 1. Login (crea cuenta gratis si no tienes)
fly auth login

# 2. Crear app
fly launch --no-deploy

# 3. Crear volumen persistente (1GB gratis)
fly volumes create pc_prices_data --size 1 --region mia

# 4. Desplegar
fly deploy

# 5. Ver logs
fly logs

# 6. Ver URL
fly status
```

## Ejecutar script de carga

Una vez desplegado en Fly.io, actualiza el script:

```python
RENDER_API = "https://pc-price-scraper.fly.dev"
```

Y ejecuta:
```bash
python scripts\upload_to_render.py
```

## Ventajas de Fly.io:

- ✅ 3 VMs gratuitas (256MB RAM cada una)
- ✅ Volumen persistente de 3GB gratis
- ✅ Sin sleep (siempre activo)
- ✅ SSL automático
- ✅ Métricas y logs
- ✅ Escala automáticamente

## Costos:

- Gratis hasta 3 máquinas + 3GB storage
- Después: ~$2/mes por VM adicional
