"""
Script completo para actualizar base de datos
1. Ejecutar scrapers de MemoryKings y SercoPlus
2. Cargar productos a la base de datos
3. Mostrar estadísticas
"""
import subprocess
import json
import os
from database import Database

print("\n" + "="*80)
print("🚀 ACTUALIZACIÓN COMPLETA DE BASE DE DATOS")
print("="*80)

# Paso 1: Ejecutar MemoryKings (sin Selenium, más rápido)
print("\n📦 1. Scraping MemoryKings...")
print("-" * 80)
os.chdir("scrapers/memorykings")
result = subprocess.run(["python", "run.py"], capture_output=False)
os.chdir("../..")

if not os.path.exists("scrapers/memorykings/products.json"):
    print("❌ No se generó products.json de MemoryKings")
else:
    print("✅ MemoryKings completado")

# Paso 2: Cargar MemoryKings a DB
print("\n💾 2. Cargando MemoryKings a base de datos...")
print("-" * 80)

db = Database()

with open("scrapers/memorykings/products.json", 'r', encoding='utf-8') as f:
    mk_data = json.load(f)

mk_products = []
if 'categories' in mk_data:
    for category, products in mk_data['categories'].items():
        mk_products.extend(products)
else:
    mk_products = mk_data

print(f"   Productos a cargar: {len(mk_products)}")

loaded = 0
for product in mk_products:
    try:
        db.add_product(product)
        loaded += 1
    except Exception as e:
        pass

print(f"   ✅ Cargados: {loaded}/{len(mk_products)}")

# Paso 3: Mostrar SercoPlus status (si existe)
if os.path.exists("scrapers/sercoplus/products.json"):
    print("\n💾 3. Cargando SercoPlus a base de datos...")
    print("-" * 80)
    
    with open("scrapers/sercoplus/products.json", 'r', encoding='utf-8') as f:
        sp_data = json.load(f)
    
    sp_products = []
    if 'categories' in sp_data:
        for category, products in sp_data['categories'].items():
            sp_products.extend(products)
    else:
        sp_products = sp_data
    
    print(f"   Productos a cargar: {len(sp_products)}")
    
    loaded = 0
    for product in sp_products:
        try:
            db.add_product(product)
            loaded += 1
        except Exception as e:
            pass
    
    print(f"   ✅ Cargados: {loaded}/{len(sp_products)}")
else:
    print("\n⚠️  3. SercoPlus: No hay products.json")
    print("   Ejecuta: cd scrapers\\sercoplus && python run.py")

# Estadísticas finales
print("\n" + "="*80)
print("📊 ESTADÍSTICAS FINALES")
print("="*80)

import sqlite3
conn = sqlite3.connect('products.db')
c = conn.cursor()

c.execute('SELECT store, COUNT(*) FROM products GROUP BY store')
results = c.fetchall()

total = 0
for row in results:
    print(f"  {row[0]}: {row[1]} productos")
    total += row[1]

print(f"\n  TOTAL: {total} productos")

# Estadísticas por categoría
print(f"\n📦 Por categoría:")
c.execute('SELECT component_type, COUNT(*) FROM products GROUP BY component_type')
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]}")

conn.close()

print("\n" + "="*80)
print("✅ PROCESO COMPLETADO")
print("="*80)
print("\n💡 Para probar el API:")
print("   python main.py")
print("   http://localhost:8000/api/stores/memorykings/products")
print("   http://localhost:8000/api/stores/sercoplus/products")
