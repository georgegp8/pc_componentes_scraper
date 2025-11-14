import sqlite3

try:
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    
    # Verificar si existe la tabla
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
    if not c.fetchone():
        print("❌ Tabla 'products' no existe")
    else:
        c.execute('SELECT store, COUNT(*) FROM products GROUP BY store')
        results = c.fetchall()
        
        print("📊 Productos por tienda:")
        total = 0
        for row in results:
            print(f"  {row[0]}: {row[1]} productos")
            total += row[1]
        print(f"\n  TOTAL: {total} productos")
    
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
