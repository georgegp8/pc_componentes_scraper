"""Script para analizar formatos de stock en la base de datos"""
import sqlite3

conn = sqlite3.connect('pc_prices.db')
cursor = conn.cursor()

# Obtener formatos de stock por tienda
cursor.execute('''
    SELECT store, stock, COUNT(*) as count 
    FROM products 
    GROUP BY store, stock 
    ORDER BY store, count DESC
''')

results = cursor.fetchall()

print('\n' + '='*60)
print('ANÁLISIS DE FORMATOS DE STOCK POR TIENDA')
print('='*60 + '\n')

current_store = None
for store, stock, count in results:
    store_display = store if store else "(null)"
    stock_display = repr(stock) if stock else "(null)"
    
    if store_display != current_store:
        print(f'\n🏪 {store_display.upper()}:')
        current_store = store_display
    
    print(f'   {stock_display:35} → {count:4} productos')

# Resumen de formatos únicos
cursor.execute('''
    SELECT DISTINCT stock 
    FROM products 
    ORDER BY stock
''')

unique_stocks = cursor.fetchall()

print('\n' + '='*60)
print('FORMATOS ÚNICOS DE STOCK EN TODA LA BD:')
print('='*60)
for (stock,) in unique_stocks:
    print(f'  - {repr(stock)}')

# Contar productos sin stock o con stock "unknown"
cursor.execute('''
    SELECT store, COUNT(*) as count
    FROM products
    WHERE stock IS NULL OR stock = '' OR stock = 'unknown'
    GROUP BY store
''')

problematic = cursor.fetchall()
if problematic:
    print('\n' + '='*60)
    print('⚠️  PRODUCTOS CON STOCK PROBLEMÁTICO:')
    print('='*60)
    for store, count in problematic:
        print(f'  {store}: {count} productos')

conn.close()
