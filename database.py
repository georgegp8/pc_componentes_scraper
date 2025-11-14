"""
Database Module
Handles all database operations for the PC price scraper
"""

import sqlite3
from typing import List, Dict, Optional
from datetime import datetime
import json

class Database:
    """SQLite database handler for PC component prices"""
    
    def __init__(self, db_path: str = "pc_prices.db"):
        self.db_path = db_path
    
    def get_connection(self):
        """Creates and returns a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initializes the database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create products table with improved schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                normalized_name TEXT,
                component_type TEXT,
                brand TEXT,
                sku TEXT,
                price_usd REAL NOT NULL,
                price_local REAL,
                currency TEXT,
                stock TEXT,
                store TEXT NOT NULL,
                source_url TEXT UNIQUE,
                image_url TEXT,
                last_scraped TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                metadata TEXT
            )
        """)
        
        # Add image_url column if it doesn't exist (migration)
        try:
            cursor.execute("ALTER TABLE products ADD COLUMN image_url TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Create indexes for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_name ON products(name)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_normalized_name ON products(normalized_name)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_component_type ON products(component_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_brand ON products(brand)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_store ON products(store)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_price ON products(price_usd)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sku ON products(sku)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_active ON products(is_active)
        """)
        
        # Create price history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                price_usd REAL NOT NULL,
                price_local REAL,
                stock TEXT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        
        # Create product matching table for cross-store comparison
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
        
        # Create scraping schedule table
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
        
        # Create scraping logs table
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
        conn.close()
    
    def insert_product(self, product: Dict) -> bool:
        """
        Inserts or updates a product in the database
        
        Args:
            product: Dictionary with product information
            
        Returns:
            True if successful, False otherwise
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Convert metadata to JSON if exists
            metadata_json = None
            if product.get('metadata'):
                metadata_json = json.dumps(product['metadata'])
            
            # Check if product already exists (by source_url or SKU+store)
            existing = None
            
            # First try by source URL (most reliable)
            if product.get('source_url'):
                cursor.execute("""
                    SELECT id, price_usd, price_local, stock FROM products 
                    WHERE source_url = ?
                """, (product['source_url'],))
                existing = cursor.fetchone()
            
            # If not found and has SKU, try by SKU+store
            if not existing and product.get('sku'):
                cursor.execute("""
                    SELECT id, price_usd, price_local, stock FROM products 
                    WHERE sku = ? AND store = ? AND is_active = 1
                """, (product['sku'], product['store']))
                existing = cursor.fetchone()
            
            if existing:
                # Update existing product
                product_id = existing['id']
                old_price_usd = existing['price_usd']
                old_price_local = existing['price_local'] if 'price_local' in existing.keys() else None
                old_stock = existing['stock'] if 'stock' in existing.keys() else None
                
                cursor.execute("""
                    UPDATE products SET
                        name = ?,
                        normalized_name = ?,
                        component_type = ?,
                        brand = ?,
                        sku = ?,
                        price_usd = ?,
                        price_local = ?,
                        currency = ?,
                        stock = ?,
                        image_url = ?,
                        last_scraped = ?,
                        metadata = ?
                    WHERE id = ?
                """, (
                    product['name'],
                    product.get('normalized_name', ''),
                    product.get('component_type', ''),
                    product.get('brand', ''),
                    product.get('sku', ''),
                    product['price_usd'],
                    product.get('price_local'),
                    product.get('currency', 'USD'),
                    product.get('stock', 'unknown'),
                    product.get('image_url', ''),
                    product.get('last_scraped', datetime.now().isoformat()),
                    metadata_json,
                    product_id
                ))
                
                # Record price history if price changed
                if (old_price_usd != product['price_usd'] or 
                    old_price_local != product.get('price_local') or
                    old_stock != product.get('stock')):
                    cursor.execute("""
                        INSERT INTO price_history (product_id, price_usd, price_local, stock)
                        VALUES (?, ?, ?, ?)
                    """, (product_id, product['price_usd'], product.get('price_local'), product.get('stock')))
                
                conn.commit()
                conn.close()
                return True
            
            # Insert new product
            cursor.execute("""
                INSERT INTO products (
                    name, normalized_name, component_type, brand, sku, 
                    price_usd, price_local, currency, stock,
                    store, source_url, image_url, last_scraped, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product['name'],
                product.get('normalized_name', ''),
                product.get('component_type', ''),
                product.get('brand', ''),
                product.get('sku', ''),
                product['price_usd'],
                product.get('price_local'),
                product.get('currency', 'USD'),
                product.get('stock', 'unknown'),
                product['store'],
                product.get('source_url', ''),
                product.get('image_url', ''),
                product.get('last_scraped', datetime.now().isoformat()),
                metadata_json
            ))
            
            # Record initial price in history
            product_id = cursor.lastrowid
            cursor.execute("""
                INSERT INTO price_history (product_id, price_usd, price_local, stock)
                VALUES (?, ?, ?, ?)
            """, (product_id, product['price_usd'], product.get('price_local'), product.get('stock')))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error inserting product: {e}")
            import traceback
            traceback.print_exc()
            conn.close()
            return False
    
    def get_products(self, skip: int = 0, limit: int = 50, filters=None) -> List[Dict]:
        """
        Gets products with optional filters
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Filter object with optional filters
            
        Returns:
            List of product dictionaries
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM products WHERE 1=1"
        params = []
        
        if filters:
            if filters.component_type:
                query += " AND component_type = ?"
                params.append(filters.component_type)
            
            if filters.brand:
                query += " AND brand = ?"
                params.append(filters.brand)
            
            if filters.min_price:
                query += " AND price_usd >= ?"
                params.append(filters.min_price)
            
            if filters.max_price:
                query += " AND price_usd <= ?"
                params.append(filters.max_price)
            
            if filters.store:
                query += " AND store = ?"
                params.append(filters.store)
        
        query += " ORDER BY last_scraped DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        products = [dict(row) for row in rows]
        conn.close()
        
        return products
    
    def count_products(self, filters=None) -> int:
        """Counts total products with optional filters"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT COUNT(*) as count FROM products WHERE 1=1"
        params = []
        
        if filters:
            if filters.component_type:
                query += " AND component_type = ?"
                params.append(filters.component_type)
            
            if filters.brand:
                query += " AND brand = ?"
                params.append(filters.brand)
            
            if filters.min_price:
                query += " AND price_usd >= ?"
                params.append(filters.min_price)
            
            if filters.max_price:
                query += " AND price_usd <= ?"
                params.append(filters.max_price)
            
            if filters.store:
                query += " AND store = ?"
                params.append(filters.store)
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        count = result['count'] if result else 0
        
        conn.close()
        return count
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Gets a specific product by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        
        product = dict(row) if row else None
        conn.close()
        
        return product
    
    def search_products(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Searches products by name
        
        Args:
            query: Search term
            limit: Maximum number of results
            
        Returns:
            List of matching products
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        search_term = f"%{query}%"
        cursor.execute("""
            SELECT * FROM products 
            WHERE name LIKE ? OR brand LIKE ? OR sku LIKE ?
            ORDER BY price_usd ASC
            LIMIT ?
        """, (search_term, search_term, search_term, limit))
        
        rows = cursor.fetchall()
        products = [dict(row) for row in rows]
        
        conn.close()
        return products
    
    def get_all_stores(self) -> List[str]:
        """Gets list of all unique stores"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT store FROM products ORDER BY store")
        rows = cursor.fetchall()
        
        stores = [row['store'] for row in rows]
        conn.close()
        
        return stores
    
    def get_all_brands(self) -> List[str]:
        """Gets list of all unique brands"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT brand FROM products 
            WHERE brand != '' 
            ORDER BY brand
        """)
        rows = cursor.fetchall()
        
        brands = [row['brand'] for row in rows]
        conn.close()
        
        return brands
    
    def get_all_types(self) -> List[str]:
        """Gets list of all component types"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT component_type FROM products 
            WHERE component_type != '' 
            ORDER BY component_type
        """)
        rows = cursor.fetchall()
        
        types = [row['component_type'] for row in rows]
        conn.close()
        
        return types
    
    def get_statistics(self) -> Dict:
        """Gets general statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total products
        cursor.execute("SELECT COUNT(*) as count FROM products")
        total_products = cursor.fetchone()['count']
        
        # Products by type
        cursor.execute("""
            SELECT component_type, COUNT(*) as count 
            FROM products 
            WHERE component_type != ''
            GROUP BY component_type
            ORDER BY count DESC
        """)
        by_type = [{'type': row['component_type'], 'count': row['count']} 
                   for row in cursor.fetchall()]
        
        # Products by store
        cursor.execute("""
            SELECT store, COUNT(*) as count 
            FROM products 
            GROUP BY store
            ORDER BY count DESC
        """)
        by_store = [{'store': row['store'], 'count': row['count']} 
                    for row in cursor.fetchall()]
        
        # Price ranges
        cursor.execute("""
            SELECT 
                MIN(price_usd) as min_price,
                MAX(price_usd) as max_price,
                AVG(price_usd) as avg_price
            FROM products
        """)
        price_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_products': total_products,
            'products_by_type': by_type,
            'products_by_store': by_store,
            'price_statistics': {
                'min': round(price_stats['min_price'], 2) if price_stats['min_price'] else 0,
                'max': round(price_stats['max_price'], 2) if price_stats['max_price'] else 0,
                'avg': round(price_stats['avg_price'], 2) if price_stats['avg_price'] else 0
            }
        }
    
    def delete_product(self, product_id: int) -> bool:
        """Deletes a product by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Delete price history first
            cursor.execute("DELETE FROM price_history WHERE product_id = ?", (product_id,))
            
            # Delete product
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            
            return success
        except Exception as e:
            print(f"Error deleting product: {e}")
            conn.close()
            return False
    
    def get_price_history(self, product_id: int) -> List[Dict]:
        """Gets price history for a product"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM price_history 
            WHERE product_id = ?
            ORDER BY recorded_at DESC
        """, (product_id,))
        
        rows = cursor.fetchall()
        history = [dict(row) for row in rows]
        
        conn.close()
        return history
