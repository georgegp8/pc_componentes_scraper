"""
Script de Limpieza de Base de Datos
Limpia duplicados, productos inactivos y datos inconsistentes
"""

import sqlite3
from database import Database
from datetime import datetime, timedelta
import sys

class DatabaseCleaner:
    def __init__(self, db_path='products.db'):
        self.db = Database(db_path)
        self.conn = self.db.get_connection()
        self.cursor = self.conn.cursor()
        
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()
    
    def get_statistics(self):
        """Obtiene estadísticas actuales de la base de datos"""
        stats = {}
        
        # Total de productos
        self.cursor.execute("SELECT COUNT(*) as count FROM products")
        stats['total_products'] = self.cursor.fetchone()['count']
        
        # Productos por tienda
        self.cursor.execute("""
            SELECT store, COUNT(*) as count 
            FROM products 
            GROUP BY store
            ORDER BY count DESC
        """)
        stats['by_store'] = dict(self.cursor.fetchall())
        
        # Productos por tipo
        self.cursor.execute("""
            SELECT component_type, COUNT(*) as count 
            FROM products 
            WHERE component_type != ''
            GROUP BY component_type
            ORDER BY count DESC
        """)
        stats['by_type'] = dict(self.cursor.fetchall())
        
        # Productos sin precio
        self.cursor.execute("""
            SELECT COUNT(*) as count FROM products 
            WHERE price_usd IS NULL OR price_usd = 0
        """)
        stats['without_price'] = self.cursor.fetchone()['count']
        
        # Productos sin imagen
        self.cursor.execute("""
            SELECT COUNT(*) as count FROM products 
            WHERE image_url IS NULL OR image_url = ''
        """)
        stats['without_image'] = self.cursor.fetchone()['count']
        
        # Productos duplicados (mismo nombre y tienda)
        self.cursor.execute("""
            SELECT name, store, COUNT(*) as count
            FROM products
            GROUP BY name, store
            HAVING COUNT(*) > 1
        """)
        stats['duplicates'] = len(self.cursor.fetchall())
        
        # Productos antiguos (más de 30 días sin actualizar)
        self.cursor.execute("""
            SELECT COUNT(*) as count FROM products
            WHERE last_scraped < datetime('now', '-30 days')
        """)
        stats['old_products'] = self.cursor.fetchone()['count']
        
        return stats
    
    def print_statistics(self, title="ESTADÍSTICAS DE BASE DE DATOS"):
        """Imprime estadísticas"""
        stats = self.get_statistics()
        
        print(f"\n{'='*70}")
        print(f"📊 {title}")
        print('='*70)
        print(f"\n📦 Total de productos: {stats['total_products']}")
        
        print(f"\n🏪 Por tienda:")
        for store, count in stats['by_store'].items():
            print(f"   - {store}: {count} productos")
        
        if stats['by_type']:
            print(f"\n🔧 Por tipo de componente:")
            for comp_type, count in stats['by_type'].items():
                print(f"   - {comp_type}: {count} productos")
        
        print(f"\n⚠️ Problemas detectados:")
        print(f"   - Sin precio: {stats['without_price']}")
        print(f"   - Sin imagen: {stats['without_image']}")
        print(f"   - Duplicados: {stats['duplicates']}")
        print(f"   - Antiguos (>30 días): {stats['old_products']}")
        
        return stats
    
    def remove_duplicates(self, dry_run=True):
        """
        Elimina productos duplicados (mismo nombre y tienda)
        Mantiene el más reciente
        """
        print(f"\n{'='*70}")
        print(f"🔍 BUSCANDO DUPLICADOS...")
        print('='*70)
        
        # Encontrar duplicados
        self.cursor.execute("""
            SELECT name, store, GROUP_CONCAT(id) as ids, COUNT(*) as count
            FROM products
            GROUP BY name, store
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        """)
        
        duplicates = self.cursor.fetchall()
        total_to_remove = 0
        
        if not duplicates:
            print("✅ No se encontraron duplicados")
            return 0
        
        print(f"📋 Encontrados {len(duplicates)} grupos de duplicados\n")
        
        for dup in duplicates:
            ids = [int(x) for x in dup['ids'].split(',')]
            count = dup['count']
            name = dup['name'][:50]
            store = dup['store']
            
            # Obtener detalles de cada duplicado
            self.cursor.execute(f"""
                SELECT id, last_scraped, price_usd, image_url
                FROM products
                WHERE id IN ({','.join('?' * len(ids))})
                ORDER BY last_scraped DESC
            """, ids)
            
            items = self.cursor.fetchall()
            keep_id = items[0]['id']  # Mantener el más reciente
            remove_ids = [item['id'] for item in items[1:]]
            
            print(f"📦 {name}... ({store})")
            print(f"   Mantener: ID {keep_id} (último scraping: {items[0]['last_scraped']})")
            print(f"   Eliminar: {len(remove_ids)} duplicado(s)")
            
            if not dry_run:
                # Eliminar price_history primero
                placeholders = ','.join('?' * len(remove_ids))
                self.cursor.execute(f"""
                    DELETE FROM price_history 
                    WHERE product_id IN ({placeholders})
                """, remove_ids)
                
                # Eliminar productos
                self.cursor.execute(f"""
                    DELETE FROM products 
                    WHERE id IN ({placeholders})
                """, remove_ids)
                
                print(f"   ✅ Eliminados {len(remove_ids)} duplicado(s)")
            
            total_to_remove += len(remove_ids)
        
        if dry_run:
            print(f"\n⚠️ MODO DRY-RUN: No se eliminó nada")
            print(f"💡 Total a eliminar: {total_to_remove} productos")
        else:
            self.conn.commit()
            print(f"\n✅ Eliminados {total_to_remove} productos duplicados")
        
        return total_to_remove
    
    def remove_without_price(self, dry_run=True):
        """Elimina productos sin precio válido"""
        print(f"\n{'='*70}")
        print(f"🔍 PRODUCTOS SIN PRECIO...")
        print('='*70)
        
        self.cursor.execute("""
            SELECT id, name, store, price_usd
            FROM products
            WHERE price_usd IS NULL OR price_usd = 0
        """)
        
        products = self.cursor.fetchall()
        
        if not products:
            print("✅ Todos los productos tienen precio")
            return 0
        
        print(f"📋 Encontrados {len(products)} productos sin precio\n")
        
        for p in products[:10]:  # Mostrar solo primeros 10
            print(f"   - ID {p['id']}: {p['name'][:60]}... ({p['store']})")
        
        if len(products) > 10:
            print(f"   ... y {len(products) - 10} más")
        
        if not dry_run:
            self.cursor.execute("""
                DELETE FROM price_history 
                WHERE product_id IN (
                    SELECT id FROM products 
                    WHERE price_usd IS NULL OR price_usd = 0
                )
            """)
            
            self.cursor.execute("""
                DELETE FROM products
                WHERE price_usd IS NULL OR price_usd = 0
            """)
            
            self.conn.commit()
            print(f"\n✅ Eliminados {len(products)} productos sin precio")
        else:
            print(f"\n⚠️ MODO DRY-RUN: No se eliminó nada")
            print(f"💡 Total a eliminar: {len(products)} productos")
        
        return len(products)
    
    def remove_old_products(self, days=60, dry_run=True):
        """Elimina productos no actualizados en X días"""
        print(f"\n{'='*70}")
        print(f"🔍 PRODUCTOS ANTIGUOS (>{days} DÍAS)...")
        print('='*70)
        
        self.cursor.execute("""
            SELECT id, name, store, last_scraped
            FROM products
            WHERE last_scraped < datetime('now', ? || ' days')
            ORDER BY last_scraped ASC
        """, (f'-{days}',))
        
        products = self.cursor.fetchall()
        
        if not products:
            print(f"✅ No hay productos sin actualizar por más de {days} días")
            return 0
        
        print(f"📋 Encontrados {len(products)} productos antiguos\n")
        
        for p in products[:10]:
            print(f"   - ID {p['id']}: {p['name'][:50]}... ({p['store']}) - {p['last_scraped']}")
        
        if len(products) > 10:
            print(f"   ... y {len(products) - 10} más")
        
        if not dry_run:
            ids = [p['id'] for p in products]
            placeholders = ','.join('?' * len(ids))
            
            self.cursor.execute(f"""
                DELETE FROM price_history 
                WHERE product_id IN ({placeholders})
            """, ids)
            
            self.cursor.execute(f"""
                DELETE FROM products 
                WHERE id IN ({placeholders})
            """, ids)
            
            self.conn.commit()
            print(f"\n✅ Eliminados {len(products)} productos antiguos")
        else:
            print(f"\n⚠️ MODO DRY-RUN: No se eliminó nada")
            print(f"💡 Total a eliminar: {len(products)} productos")
        
        return len(products)
    
    def remove_by_store(self, store_name, dry_run=True):
        """Elimina todos los productos de una tienda específica"""
        print(f"\n{'='*70}")
        print(f"🔍 PRODUCTOS DE TIENDA: {store_name}")
        print('='*70)
        
        self.cursor.execute("""
            SELECT COUNT(*) as count FROM products
            WHERE store = ?
        """, (store_name,))
        
        count = self.cursor.fetchone()['count']
        
        if count == 0:
            print(f"⚠️ No se encontraron productos de la tienda '{store_name}'")
            return 0
        
        print(f"📋 Encontrados {count} productos de {store_name}")
        
        if not dry_run:
            self.cursor.execute("""
                DELETE FROM price_history 
                WHERE product_id IN (
                    SELECT id FROM products WHERE store = ?
                )
            """, (store_name,))
            
            self.cursor.execute("""
                DELETE FROM products
                WHERE store = ?
            """, (store_name,))
            
            self.conn.commit()
            print(f"✅ Eliminados {count} productos de {store_name}")
        else:
            print(f"\n⚠️ MODO DRY-RUN: No se eliminó nada")
            print(f"💡 Total a eliminar: {count} productos")
        
        return count
    
    def vacuum_database(self):
        """Optimiza la base de datos (VACUUM)"""
        print(f"\n{'='*70}")
        print(f"🔧 OPTIMIZANDO BASE DE DATOS...")
        print('='*70)
        
        self.cursor.execute("VACUUM")
        print("✅ Base de datos optimizada")
    
    def full_cleanup(self, remove_duplicates=True, remove_no_price=True, 
                     remove_old=False, days=60, dry_run=True):
        """Limpieza completa de la base de datos"""
        print("\n" + "="*70)
        print("🧹 LIMPIEZA COMPLETA DE BASE DE DATOS")
        print("="*70)
        
        if dry_run:
            print("\n⚠️ MODO DRY-RUN ACTIVADO - No se eliminará nada")
            print("💡 Usa --execute para aplicar los cambios\n")
        
        # Estadísticas iniciales
        self.print_statistics("ANTES DE LA LIMPIEZA")
        
        total_removed = 0
        
        # Eliminar duplicados
        if remove_duplicates:
            total_removed += self.remove_duplicates(dry_run)
        
        # Eliminar sin precio
        if remove_no_price:
            total_removed += self.remove_without_price(dry_run)
        
        # Eliminar antiguos
        if remove_old:
            total_removed += self.remove_old_products(days, dry_run)
        
        # Estadísticas finales
        if not dry_run:
            self.print_statistics("DESPUÉS DE LA LIMPIEZA")
            self.vacuum_database()
        
        # Resumen
        print(f"\n{'='*70}")
        print("📊 RESUMEN DE LIMPIEZA")
        print('='*70)
        print(f"Total de productos a eliminar/eliminados: {total_removed}")
        
        if dry_run:
            print("\n💡 Para aplicar los cambios, ejecuta:")
            print("   python clean_database.py --execute")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Limpieza de base de datos')
    parser.add_argument('--execute', action='store_true', 
                       help='Ejecutar limpieza (por defecto es dry-run)')
    parser.add_argument('--db', default='products.db', 
                       help='Ruta a la base de datos (default: products.db)')
    parser.add_argument('--remove-store', 
                       help='Eliminar todos los productos de una tienda específica')
    parser.add_argument('--remove-old', action='store_true',
                       help='Eliminar productos antiguos (>60 días)')
    parser.add_argument('--days', type=int, default=60,
                       help='Días para considerar producto antiguo (default: 60)')
    parser.add_argument('--stats-only', action='store_true',
                       help='Solo mostrar estadísticas')
    
    args = parser.parse_args()
    
    cleaner = DatabaseCleaner(args.db)
    
    # Solo estadísticas
    if args.stats_only:
        cleaner.print_statistics()
        return
    
    # Eliminar tienda específica
    if args.remove_store:
        dry_run = not args.execute
        cleaner.print_statistics("ANTES DE ELIMINAR")
        cleaner.remove_by_store(args.remove_store, dry_run)
        if not dry_run:
            cleaner.print_statistics("DESPUÉS DE ELIMINAR")
            cleaner.vacuum_database()
        return
    
    # Limpieza completa
    cleaner.full_cleanup(
        remove_duplicates=True,
        remove_no_price=True,
        remove_old=args.remove_old,
        days=args.days,
        dry_run=not args.execute
    )


if __name__ == "__main__":
    main()
