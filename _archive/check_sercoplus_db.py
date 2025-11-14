import sqlite3

conn = sqlite3.connect('products.db')
cursor = conn.cursor()

# Check SercoPlus products
cursor.execute('SELECT COUNT(*) FROM products WHERE store = "sercoplus"')
count = cursor.fetchone()[0]
print(f'Productos SercoPlus en DB: {count}')

if count > 0:
    cursor.execute('SELECT name, price_usd, image_url, stock FROM products WHERE store = "sercoplus" LIMIT 5')
    products = cursor.fetchall()
    print('\nEjemplos:')
    for i, p in enumerate(products):
        print(f'{i+1}. {p[0][:60]}')
        print(f'   Precio: ${p[1]}')
        print(f'   Imagen: {"✓" if p[2] else "✗ NULL"}')
        print(f'   Stock: {p[3]}')
        print()

conn.close()
