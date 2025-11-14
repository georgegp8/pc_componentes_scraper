"""Script para estandarizar formatos de stock a '+10'"""
import sqlite3

conn = sqlite3.connect('pc_prices.db')
cursor = conn.cursor()

print('\n' + '='*60)
print('ESTANDARIZANDO FORMATOS DE STOCK')
print('='*60 + '\n')

# Cambiar '10+' a '+10' (SercoPlus)
cursor.execute("UPDATE products SET stock = '+10' WHERE stock = '10+'")
sercoplus_updated = cursor.rowcount
print(f"✅ SercoPlus: {sercoplus_updated} productos actualizados ('10+' → '+10')")

# Cambiar '>10' a '+10' (CycComputer)
cursor.execute("UPDATE products SET stock = '+10' WHERE stock = '>10'")
cyccomputer_updated = cursor.rowcount
print(f"✅ CycComputer: {cyccomputer_updated} productos actualizados ('>10' → '+10')")

# Commit changes
conn.commit()

# Verificar resultado
cursor.execute('''
    SELECT store, stock, COUNT(*) as count 
    FROM products 
    WHERE stock = '+10'
    GROUP BY store
    ORDER BY store
''')

results = cursor.fetchall()

print('\n' + '='*60)
print('PRODUCTOS CON STOCK +10:')
print('='*60)
for store, stock, count in results:
    print(f"  {store}: {count} productos")

# Verificar que no queden formatos antiguos
cursor.execute('''
    SELECT stock, COUNT(*) as count
    FROM products
    WHERE stock IN ('10+', '>10')
    GROUP BY stock
''')

old_formats = cursor.fetchall()
if old_formats:
    print('\n⚠️  FORMATOS ANTIGUOS RESTANTES:')
    for stock, count in old_formats:
        print(f"  {stock}: {count} productos")
else:
    print('\n✅ No quedan formatos antiguos (10+ o >10)')

# Mostrar resumen final de formatos únicos
cursor.execute('''
    SELECT DISTINCT stock 
    FROM products 
    ORDER BY 
        CASE 
            WHEN stock = '0' THEN 0
            WHEN stock = '+10' THEN 999
            ELSE CAST(stock AS INTEGER)
        END
''')

unique_stocks = cursor.fetchall()

print('\n' + '='*60)
print('FORMATOS DE STOCK DESPUÉS DE ESTANDARIZACIÓN:')
print('='*60)
for (stock,) in unique_stocks:
    cursor.execute('SELECT COUNT(*) FROM products WHERE stock = ?', (stock,))
    count = cursor.fetchone()[0]
    print(f"  '{stock}' → {count} productos")

conn.close()

print('\n✅ Estandarización completada\n')
