"""
Script para subir productos de la base de datos local a una API remota
Funciona con cualquier API compatible (Render, PythonAnywhere, etc.)
"""
import sqlite3
import requests
import time
from typing import List, Dict

# Configuración - Cambiar según tu API remota
API_URL = "https://pc-componentes-scraper.onrender.com"  # Cambiar a tu URL
LOCAL_DB = "pc_prices.db"

def get_local_products() -> List[Dict]:
    """Obtiene todos los productos de la BD local"""
    conn = sqlite3.connect(LOCAL_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM products 
        ORDER BY store, component_type
    """)
    
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    print(f"📦 Encontrados {len(products)} productos locales")
    return products

def upload_product(product: Dict) -> bool:
    """Sube un producto a la API remota usando el endpoint POST /api/products"""
    try:
        # Mapear campos de BD a API
        payload = {
            "name": product["name"],
            "price": float(product["price_usd"]),
            "currency": product.get("currency", "USD"),
            "url": product["source_url"],
            "store_name": product["store"],
            "component_type": product.get("component_type"),
            "image_url": product.get("image_url"),
            "brand": product.get("brand"),
            "stock_status": product.get("stock", "available"),
            "sku": product.get("sku")
        }
        
        response = requests.post(
            f"{API_URL}/api/products",
            json=payload,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            return True
        else:
            print(f"   Status: {response.status_code}, Response: {response.text[:100]}")
            return False
    
    except Exception as e:
        print(f"   Exception: {e}")
        return False

def main():
    print("🚀 Iniciando carga de productos a API remota...")
    print(f"🎯 Destino: {API_URL}")
    
    # Obtener productos locales
    products = get_local_products()
    
    # Agrupar por tienda
    by_store = {}
    for p in products:
        store = p["store"]
        by_store.setdefault(store, []).append(p)
    
    print(f"\n📊 Productos por tienda:")
    for store, prods in by_store.items():
        print(f"  - {store}: {len(prods)} productos")
    
    # Subir productos
    print(f"\n⬆️  Subiendo productos...")
    success = 0
    failed = 0
    
    for i, product in enumerate(products, 1):
        if upload_product(product):
            success += 1
            print(f"✅ [{i}/{len(products)}] {product['name'][:50]}")
        else:
            failed += 1
            print(f"❌ [{i}/{len(products)}] Error: {product['name'][:50]}")
        
        # Rate limiting: 1 request por segundo
        if i % 10 == 0:
            print(f"⏸️  Pausa (evitar sobrecarga)...")
            time.sleep(2)
        else:
            time.sleep(0.5)
    
    print(f"\n✨ Completado!")
    print(f"  ✅ Exitosos: {success}")
    print(f"  ❌ Fallidos: {failed}")
    print(f"  📊 Total: {len(products)}")

if __name__ == "__main__":
    main()
