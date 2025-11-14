"""
Database Migration Script
Migrates existing database to new schema or creates fresh database
"""

import sqlite3
import os
from datetime import datetime

def backup_database(db_path: str):
    """Creates a backup of the existing database"""
    if os.path.exists(db_path):
        backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✓ Backup creado: {backup_path}")
        return backup_path
    return None

def check_schema_version(db_path: str) -> str:
    """Checks what schema version the database has"""
    if not os.path.exists(db_path):
        return "none"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if products table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
        if not cursor.fetchone():
            conn.close()
            return "none"
        
        # Check if normalized_name column exists
        cursor.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'normalized_name' not in columns:
            conn.close()
            return "old"
        
        conn.close()
        return "current"
        
    except Exception as e:
        print(f"Error checking schema: {e}")
        conn.close()
        return "unknown"

def migrate_old_to_new(db_path: str):
    """Migrates old schema to new schema"""
    print("📊 Migrando base de datos antigua al nuevo esquema...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check current columns
        cursor.execute("PRAGMA table_info(products)")
        existing_columns = {row[1]: row for row in cursor.fetchall()}
        
        # Add missing columns
        columns_to_add = {
            'normalized_name': 'TEXT',
            'component_type': 'TEXT',
            'currency': 'TEXT',
            'source_url': 'TEXT',
            'is_active': 'INTEGER DEFAULT 1',
            'metadata': 'TEXT'
        }
        
        for col_name, col_type in columns_to_add.items():
            if col_name not in existing_columns:
                print(f"  → Agregando columna: {col_name}")
                cursor.execute(f"ALTER TABLE products ADD COLUMN {col_name} {col_type}")
        
        # Create indexes if they don't exist
        indexes = [
            ("idx_normalized_name", "products(normalized_name)"),
            ("idx_component_type", "products(component_type)"),
            ("idx_active", "products(is_active)"),
        ]
        
        for idx_name, idx_def in indexes:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {idx_def}")
            except:
                pass  # Index might already exist
        
        # Create new tables if they don't exist
        print("  → Creando tablas adicionales...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id_1 INTEGER,
                product_id_2 INTEGER,
                confidence REAL DEFAULT 0.0,
                match_method TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id_1) REFERENCES products(id),
                FOREIGN KEY (product_id_2) REFERENCES products(id),
                UNIQUE(product_id_1, product_id_2)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraping_schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store_name TEXT NOT NULL,
                url TEXT NOT NULL,
                category TEXT,
                frequency_hours INTEGER DEFAULT 24,
                last_run TIMESTAMP,
                next_run TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraping_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store_name TEXT NOT NULL,
                url TEXT,
                products_found INTEGER,
                products_saved INTEGER,
                status TEXT,
                error_message TEXT,
                duration_seconds REAL,
                started_at TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        
        conn.commit()
        print("✓ Migración completada exitosamente")
        
    except Exception as e:
        print(f"✗ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False
    
    finally:
        conn.close()
    
    return True

def create_fresh_database(db_path: str):
    """Creates a fresh database with the current schema"""
    print("📊 Creando nueva base de datos...")
    
    from database import Database
    db = Database(db_path)
    db.init_db()
    
    print("✓ Base de datos creada exitosamente")
    return True

def main():
    """Main migration function"""
    db_path = "pc_prices.db"
    
    print("=" * 60)
    print("  MIGRACIÓN DE BASE DE DATOS")
    print("=" * 60)
    print()
    
    # Check schema version
    schema_version = check_schema_version(db_path)
    
    if schema_version == "none":
        print("ℹ No se encontró base de datos existente")
        print()
        create_fresh_database(db_path)
        
    elif schema_version == "old":
        print("⚠ Se encontró base de datos con esquema antiguo")
        print()
        
        # Ask for confirmation
        response = input("¿Deseas migrar la base de datos existente? (s/n): ")
        if response.lower() == 's':
            # Backup first
            backup_path = backup_database(db_path)
            
            # Migrate
            if migrate_old_to_new(db_path):
                print()
                print("✓ Migración completada")
                print(f"  Backup guardado en: {backup_path}")
            else:
                print()
                print("✗ Error en la migración")
                if backup_path:
                    print(f"  Puedes restaurar desde: {backup_path}")
        else:
            print()
            print("Migración cancelada")
            print("Para crear una base de datos nueva, elimina o renombra 'pc_prices.db'")
            
    elif schema_version == "current":
        print("✓ La base de datos ya está actualizada")
        
    else:
        print("⚠ No se pudo determinar la versión del esquema")
        print()
        response = input("¿Deseas eliminar y crear una base de datos nueva? (s/n): ")
        if response.lower() == 's':
            backup_database(db_path)
            os.remove(db_path)
            create_fresh_database(db_path)
    
    print()
    print("=" * 60)
    print()

if __name__ == "__main__":
    main()
