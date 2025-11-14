"""
Verificar que tenemos procesadores Intel Core para comparar con SercoPlus
"""
import json

# Leer datos
with open('memorykings_all_products.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

procesadores = data['categories']['procesadores']

# Filtrar Intel Core
intel_core = [p for p in procesadores if 'intel' in p['name'].lower() and 'core' in p['name'].lower()]

print("="*70)
print(f"🔍 PROCESADORES INTEL CORE CAPTURADOS: {len(intel_core)}")
print("="*70)

# Agrupar por categoría
by_category = {}
for p in intel_core:
    cat = p['category']
    if cat not in by_category:
        by_category[cat] = []
    by_category[cat].append(p)

for cat, procs in sorted(by_category.items()):
    print(f"\n{cat} ({len(procs)} productos):")
    for p in procs:
        # Extraer modelo (i3, i5, i7, i9)
        name_lower = p['name'].lower()
        if 'core i3' in name_lower or 'i3-' in name_lower:
            model = 'i3'
        elif 'core i5' in name_lower or 'i5-' in name_lower:
            model = 'i5'
        elif 'core i7' in name_lower or 'i7-' in name_lower:
            model = 'i7'
        elif 'core i9' in name_lower or 'i9-' in name_lower:
            model = 'i9'
        elif 'core ultra' in name_lower:
            model = 'Ultra'
        else:
            model = '???'
        
        print(f"  [{model:5}] ${p['price_usd']:6.0f} - {p['name'][:60]}")

print("\n" + "="*70)
print("📊 RESUMEN POR MODELO:")
print("="*70)

# Contar por modelo
models = {}
for p in intel_core:
    name_lower = p['name'].lower()
    if 'core i3' in name_lower or 'i3-' in name_lower:
        model = 'Core i3'
    elif 'core i5' in name_lower or 'i5-' in name_lower:
        model = 'Core i5'
    elif 'core i7' in name_lower or 'i7-' in name_lower:
        model = 'Core i7'
    elif 'core i9' in name_lower or 'i9-' in name_lower:
        model = 'Core i9'
    elif 'core ultra' in name_lower:
        model = 'Core Ultra'
    else:
        model = 'Otro'
    
    models[model] = models.get(model, 0) + 1

for model, count in sorted(models.items()):
    print(f"  {model}: {count} procesadores")

print("\n✅ Ahora tenemos Intel Core i3/i5/i7/i9/Ultra para comparar con SercoPlus!")
