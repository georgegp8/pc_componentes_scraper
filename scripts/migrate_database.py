"""
Script de Migración de Base de Datos
Agrega la columna image_url a la tabla products
"""

import sqlite3

def migrate_database(db_path='products.db'):
    print(f"\n{'='*70}")
    print("🔧 MIGRACIÓN DE BASE DE DATOS")
    print('='*70)
    print(f"Base de datos: {db_path}\n")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(products)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'image_url' in columns:
            print("✅ La columna 'image_url' ya existe")
        else:
            print("➕ Agregando columna 'image_url'...")
            cursor.execute("ALTER TABLE products ADD COLUMN image_url TEXT")
            conn.commit()
            print("✅ Columna 'image_url' agregada correctamente")
        
        # Mostrar estructura actual
        cursor.execute("PRAGMA table_info(products)")
        columns = cursor.fetchall()
        
        print(f"\n📋 Estructura de tabla 'products':")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # Contar productos
        cursor.execute("SELECT COUNT(*) as count FROM products")
        count = cursor.fetchone()[0]
        print(f"\n📦 Total de productos: {count}")
        
        # Contar productos con imagen
        cursor.execute("""
            SELECT COUNT(*) as count FROM products 
            WHERE image_url IS NOT NULL AND image_url != ''
        """)
        with_image = cursor.fetchone()[0]
        print(f"🖼️  Productos con imagen: {with_image} ({with_image/count*100:.1f}%)" if count > 0 else "🖼️  Productos con imagen: 0")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()
    
    print(f"\n{'='*70}")
    print("✅ MIGRACIÓN COMPLETADA")
    print('='*70)

if __name__ == "__main__":
    import sys
    
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'products.db'
    migrate_database(db_path)
