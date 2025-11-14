# 🧹 Guía de Limpieza de Base de Datos

**Fecha:** 13 de Noviembre 2025  
**Script:** `clean_database.py`

---

## 📋 Descripción

Script completo para mantener la base de datos limpia y optimizada. Elimina duplicados, productos sin precio, productos antiguos, y optimiza el almacenamiento.

---

## 🚀 Uso Básico

### 1. Ver Estadísticas (Sin Modificar)

```powershell
.\venv\Scripts\Activate.ps1; python clean_database.py --stats-only
```

**Muestra:**
- Total de productos
- Productos por tienda
- Productos por tipo de componente
- Problemas detectados (duplicados, sin precio, antiguos)

---

### 2. Análisis Completo (Dry-Run)

```powershell
.\venv\Scripts\Activate.ps1; python clean_database.py
```

**Analiza sin eliminar:**
- ✅ Duplicados (mismo nombre y tienda)
- ✅ Productos sin precio válido
- ⚠️ Productos antiguos (solo con `--remove-old`)

**Output:**
```
📊 ESTADÍSTICAS DE BASE DE DATOS
===================================================================

📦 Total de productos: 288

🏪 Por tienda:
   - memorykings: 288 productos

🔧 Por tipo de componente:
   - almacenamiento: 103 productos
   - memorias-ram: 42 productos
   - procesadores: 68 productos
   - tarjetas-video: 75 productos

⚠️ Problemas detectados:
   - Sin precio: 0
   - Sin imagen: 5
   - Duplicados: 3
   - Antiguos (>30 días): 0
```

---

### 3. Limpieza Completa (Ejecutar Cambios)

```powershell
.\venv\Scripts\Activate.ps1; python clean_database.py --execute
```

**Elimina:**
- ✅ Duplicados (mantiene el más reciente)
- ✅ Productos sin precio
- ✅ Optimiza la base de datos (VACUUM)

---

## 🎯 Operaciones Específicas

### Eliminar Productos de una Tienda

```powershell
# Dry-run (analizar)
.\venv\Scripts\Activate.ps1; python clean_database.py --remove-store memorykings

# Ejecutar eliminación
.\venv\Scripts\Activate.ps1; python clean_database.py --remove-store memorykings --execute
```

**Casos de uso:**
- Migración de scraper (eliminar datos antiguos de una tienda)
- Tienda descontinuada
- Datos incorrectos de scraping fallido

---

### Eliminar Productos Antiguos

```powershell
# Eliminar productos sin actualizar por más de 60 días
.\venv\Scripts\Activate.ps1; python clean_database.py --remove-old --execute

# Eliminar productos sin actualizar por más de 30 días
.\venv\Scripts\Activate.ps1; python clean_database.py --remove-old --days 30 --execute
```

**Casos de uso:**
- Limpiar productos descontinuados
- Mantener solo datos recientes
- Reducir tamaño de base de datos

---

### Base de Datos Alternativa

```powershell
# Limpiar base de datos de prueba
.\venv\Scripts\Activate.ps1; python clean_database.py --db test.db --execute

# Analizar base de datos de producción
.\venv\Scripts\Activate.ps1; python clean_database.py --db production.db --stats-only
```

---

## 🔍 Detalles de Limpieza

### 1. Eliminación de Duplicados

**Criterio:** Mismo nombre + misma tienda  
**Acción:** Mantiene el producto con `last_scraped` más reciente

**Ejemplo:**
```
📦 PROCESADOR AMD RYZEN 5 5600X... (memorykings)
   Mantener: ID 125 (último scraping: 2025-11-13 10:30:00)
   Eliminar: 2 duplicado(s)
   ✅ Eliminados 2 duplicado(s)
```

**Seguridad:**
- ✅ Mantiene historial de precios del producto conservado
- ✅ Elimina historial de precios de duplicados
- ⚠️ Irreversible - revisar dry-run primero

---

### 2. Productos Sin Precio

**Criterio:** `price_usd IS NULL` o `price_usd = 0`  
**Acción:** Elimina completamente (no son útiles para comparación)

**Ejemplo:**
```
📋 Encontrados 5 productos sin precio

   - ID 45: PRODUCTO SIN PRECIO DISPONIBLE... (memorykings)
   - ID 78: ITEM AGOTADO SIN PRECIO... (sercoplus)
   ... y 3 más

✅ Eliminados 5 productos sin precio
```

**Razón:**
- Sin precio no se pueden comparar
- Ocupan espacio innecesario
- Pueden ser productos descontinuados

---

### 3. Productos Antiguos

**Criterio:** `last_scraped < datetime('now', '-X days')`  
**Acción:** Elimina productos no actualizados por X días

**Ejemplo (60 días):**
```
📋 Encontrados 12 productos antiguos

   - ID 10: PRODUCTO VIEJO... (memorykings) - 2025-09-01 08:00:00
   - ID 25: ITEM DESCONTINUADO... (sercoplus) - 2025-08-15 12:30:00
   ... y 10 más

✅ Eliminados 12 productos antiguos
```

**Ventajas:**
- Mantiene solo datos actuales
- Reduce tamaño de base de datos
- Mejora rendimiento de queries

**Precaución:**
- Solo usar si el scraping es frecuente
- Verificar que no elimine productos válidos
- Default: 60 días (ajustable con `--days`)

---

### 4. Optimización (VACUUM)

**Acción:** Reorganiza la base de datos para recuperar espacio

**Beneficios:**
- ✅ Reduce tamaño de archivo .db
- ✅ Mejora velocidad de queries
- ✅ Desfragmenta índices

**Nota:** Se ejecuta automáticamente después de limpieza con `--execute`

---

## 📊 Casos de Uso

### Caso 1: Mantenimiento Semanal

```powershell
# Ejecutar cada semana para mantener BD limpia
.\venv\Scripts\Activate.ps1; python clean_database.py --execute
```

**Limpia:**
- Duplicados generados por múltiples ejecuciones
- Productos que perdieron precio
- Optimiza almacenamiento

---

### Caso 2: Migración de Scraper

**Escenario:** Cambiaste el scraper de MemoryKings y quieres borrar datos antiguos

```powershell
# 1. Analizar datos actuales
.\venv\Scripts\Activate.ps1; python clean_database.py --stats-only

# 2. Eliminar productos de MemoryKings
.\venv\Scripts\Activate.ps1; python clean_database.py --remove-store memorykings --execute

# 3. Ejecutar nuevo scraper
cd scrapers\memorykings
.\venv\Scripts\Activate.ps1; python run.py

# 4. Cargar nuevos datos
.\venv\Scripts\Activate.ps1; python load_memorykings_to_db.py
```

---

### Caso 3: Limpieza Profunda

**Escenario:** Base de datos muy grande con muchos productos antiguos

```powershell
# 1. Ver estadísticas
.\venv\Scripts\Activate.ps1; python clean_database.py --stats-only

# 2. Eliminar duplicados y sin precio
.\venv\Scripts\Activate.ps1; python clean_database.py --execute

# 3. Eliminar productos antiguos (>30 días)
.\venv\Scripts\Activate.ps1; python clean_database.py --remove-old --days 30 --execute

# 4. Ver estadísticas finales
.\venv\Scripts\Activate.ps1; python clean_database.py --stats-only
```

---

### Caso 4: Preparar para Producción

**Escenario:** Antes de deployer API en servidor

```powershell
# 1. Backup de base de datos
Copy-Item products.db products.backup.db

# 2. Limpieza completa
.\venv\Scripts\Activate.ps1; python clean_database.py --execute

# 3. Eliminar productos antiguos
.\venv\Scripts\Activate.ps1; python clean_database.py --remove-old --execute

# 4. Verificar integridad
.\venv\Scripts\Activate.ps1; python clean_database.py --stats-only

# 5. Si algo sale mal, restaurar backup
# Copy-Item products.backup.db products.db
```

---

## ⚠️ Precauciones

### 1. Siempre Hacer Dry-Run Primero

```powershell
# ❌ NO hagas esto directamente
.\venv\Scripts\Activate.ps1; python clean_database.py --remove-old --execute

# ✅ Primero analiza
.\venv\Scripts\Activate.ps1; python clean_database.py --remove-old
# Luego ejecuta
.\venv\Scripts\Activate.ps1; python clean_database.py --remove-old --execute
```

---

### 2. Hacer Backup

```powershell
# Antes de limpieza importante
Copy-Item products.db products.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss').db
```

---

### 3. Verificar Resultados

```powershell
# Después de limpieza, verificar estadísticas
.\venv\Scripts\Activate.ps1; python clean_database.py --stats-only
```

---

## 🆕 Nuevas Categorías - SercoPlus

### Motherboards Agregadas

```python
categories = {
    'procesadores': 'https://sercoplus.com/37-procesadores',
    'memorias-ram': 'https://sercoplus.com/55-memorias-ram',
    'almacenamiento': 'https://sercoplus.com/39-almacenamiento',
    'disco-duro': 'https://sercoplus.com/40-disco-duro',
    'mainboard-intel': 'https://sercoplus.com/39-mainboard-intel',  # ✨ NUEVO
    'mainboard-amd': 'https://sercoplus.com/40-mainboard-amd'        # ✨ NUEVO
}
```

### Ejecutar Scraping con Motherboards

```powershell
# 1. Ir a directorio de SercoPlus
cd scrapers\sercoplus

# 2. Activar venv y ejecutar scraper
.\..\..\venv\Scripts\Activate.ps1; python run.py

# 3. Cargar a base de datos
cd ..\..
.\venv\Scripts\Activate.ps1; python load_sercoplus_to_db.py
```

**Resultado esperado:**
```
📦 Total de productos: ~450
   - procesadores: 60
   - memorias-ram: 50
   - almacenamiento: 80
   - disco-duro: 40
   - mainboard-intel: 120  ⬅️ NUEVO
   - mainboard-amd: 100    ⬅️ NUEVO
```

---

## 🔄 Workflow Completo

### Actualización Semanal de Base de Datos

```powershell
# 1. Backup
Copy-Item products.db "products.backup.$(Get-Date -Format 'yyyyMMdd').db"

# 2. Ver estado actual
.\venv\Scripts\Activate.ps1; python clean_database.py --stats-only

# 3. Limpiar duplicados y sin precio
.\venv\Scripts\Activate.ps1; python clean_database.py --execute

# 4. Scraping de tiendas
cd scrapers\memorykings
.\..\..\venv\Scripts\Activate.ps1; python run.py
cd ..\sercoplus
.\..\..\venv\Scripts\Activate.ps1; python run.py
cd ..\..

# 5. Cargar datos
.\venv\Scripts\Activate.ps1; python load_memorykings_to_db.py
.\venv\Scripts\Activate.ps1; python load_sercoplus_to_db.py

# 6. Limpieza final
.\venv\Scripts\Activate.ps1; python clean_database.py --execute

# 7. Estadísticas finales
.\venv\Scripts\Activate.ps1; python clean_database.py --stats-only
```

---

## 📈 Métricas de Éxito

Después de limpieza, deberías ver:

✅ **0 duplicados**  
✅ **0 productos sin precio**  
✅ **95%+ con imagen**  
✅ **100% actualizados en última semana**  
✅ **Base de datos optimizada**

---

**Generado por:** GitHub Copilot  
**Última actualización:** 2025-11-13
