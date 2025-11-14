# Desplegar en PythonAnywhere (100% Gratis + Persistente + Sin Sleep)

## ⚡ Guía Rápida (10 minutos)

### 1️⃣ Crear cuenta (2 min)

1. Ve a https://www.pythonanywhere.com/registration/register/beginner/
2. Username: elige uno (ejemplo: `georgepc`)
3. Email + Password
4. Verifica email
5. ✅ Login

### 2️⃣ Subir código desde GitHub (3 min)

En **Consoles** > **Bash**:

```bash
# Clonar repositorio
git clone https://github.com/georgegp8/pc_componentes_scraper.git
cd pc_componentes_scraper

# Instalar dependencias
pip3.11 install --user -r requirements.txt
```

⏳ Espera 2-3 minutos mientras instala.

### 3️⃣ Crear Web App (2 min)

1. **Web tab** > **Add a new web app**
2. **Manual configuration** (Python 3.11)
3. ✅ App creada

### 4️⃣ Configurar WSGI (2 min)

En **Web tab**, busca:
- **Code** section
- Click en `/var/www/TUUSUARIO_pythonanywhere_com_wsgi.py`

**Reemplaza TODO el contenido con:**

```python
import sys
import os

# Agregar proyecto al path
username = os.environ.get('USER', 'TUUSUARIO')  # Se detecta automático
project_home = f'/home/{username}/pc_componentes_scraper'

if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Configurar variables de entorno
os.environ['DATABASE_PATH'] = f'{project_home}/pc_prices.db'
os.environ['LOG_LEVEL'] = 'INFO'

# Importar app FastAPI
from main import app as application
```

⚠️ **IMPORTANTE:** Si tu username es diferente, reemplaza donde dice `TUUSUARIO`

**Guarda** el archivo (Ctrl+S o botón Save)

### 5️⃣ Configurar virtualenv (1 min)

En **Web tab** > **Virtualenv** section:

```
/home/TUUSUARIO/.local
```

O déjalo vacío si instalaste con `pip3.11 install --user`

### 6️⃣ Activar app (30 seg)

En **Web tab**:
- Click botón verde **Reload**
- 🎉 Tu API está en: `https://TUUSUARIO.pythonanywhere.com`

### 7️⃣ Verificar funcionamiento (30 seg)

Abre en navegador:
- https://TUUSUARIO.pythonanywhere.com/
- https://TUUSUARIO.pythonanywhere.com/docs
- https://TUUSUARIO.pythonanywhere.com/api/stores

Deberías ver:
```json
{"total": 0, "stores": []}
```

### 8️⃣ Subir datos desde tu PC local

Actualiza el script:

```python
# En scripts/upload_to_render.py línea 10
RENDER_API = "https://TUUSUARIO.pythonanywhere.com"
```

Ejecuta:
```powershell
$env:PYTHONIOENCODING="utf-8"; python scripts\upload_to_render.py
```

⏳ Tardará 15-20 minutos en subir los 1873 productos.

---

## 🎯 Características

| Feature | Valor |
|---------|-------|
| **Costo** | $0 (gratis para siempre) |
| **Tarjeta** | ❌ No requerida |
| **Persistencia** | ✅ Automática (SQLite permanente) |
| **Sleep** | ❌ Nunca se duerme |
| **SSL** | ✅ HTTPS incluido |
| **RAM** | 512MB |
| **Storage** | 512MB |
| **Requests/día** | 100,000 |
| **Setup** | 10 minutos |

---

## 🐛 Solución de problemas

### Error: ModuleNotFoundError

```bash
cd ~/pc_componentes_scraper
pip3.11 install --user -r requirements.txt
```

Luego **Reload** en Web tab.

### Error: Database locked

PythonAnywhere no permite múltiples workers. Esto es normal, SQLite funciona bien con 1 worker.

### Ver logs de errores

**Web tab** > **Log files** > Click en `error.log`

### Actualizar código

```bash
cd ~/pc_componentes_scraper
git pull origin main
```

Luego **Reload** en Web tab.

---

## 📊 Monitoreo

- **Access log:** Ver requests entrantes
- **Error log:** Ver errores de Python
- **Server log:** Ver inicio/parada del servidor

Todos en **Web tab** > **Log files**

---

## 🔄 Mantener actualizado

Cuando hagas cambios en GitHub:

```bash
# En Bash console de PythonAnywhere
cd ~/pc_componentes_scraper
git pull
```

Luego **Reload** en Web tab.

---

## 🚀 Próximos pasos

Una vez que tengas datos:

1. ✅ API funcionando: `https://TUUSUARIO.pythonanywhere.com/api/products`
2. ✅ Datos persistentes (nunca se pierden)
3. ✅ Siempre activo (sin cold starts)
4. 📱 Conectar tu app móvil iOS a esta URL

---

## 💡 Ventajas vs Render

| Feature | PythonAnywhere | Render Free |
|---------|----------------|-------------|
| Setup | 10 min | 30 min+ |
| Persistencia | ✅ Auto | ⚠️ Manual |
| Sleep | ❌ Nunca | ✅ 15 min |
| Cold start | 0s | 30-60s |
| Tarjeta | No | No |
| Mantenimiento | Cero | Alto |

**Conclusión:** PythonAnywhere es perfecto para tu proyecto.
