"""
Script de prueba para endpoints por tienda
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Imprime un título de sección"""
    print("\n" + "="*80)
    print(f"🔍 {title}")
    print("="*80 + "\n")

def test_memorykings():
    """Prueba endpoints de MemoryKings"""
    print_section("MEMORYKINGS - Productos")
    
    # Todos los productos (primeros 5)
    response = requests.get(f"{BASE_URL}/api/stores/memorykings/products?limit=5")
    if response.status_code == 200:
        data = response.json()
        print(f"Total productos: {data['total']}")
        print(f"Mostrando: {data['count']}/{data['total']}")
        print("\nPrimeros 5 productos:")
        for i, p in enumerate(data['products'][:5], 1):
            print(f"  {i}. {p['name'][:60]}")
            print(f"     Precio: ${p['price_usd']} | Stock: {p['stock']} | Marca: {p.get('brand', 'N/A')}")
    else:
        print(f"❌ Error: {response.status_code}")
    
    # Solo procesadores Intel
    print("\n" + "-"*80)
    print("Procesadores Intel de MemoryKings:")
    print("-"*80)
    response = requests.get(
        f"{BASE_URL}/api/stores/memorykings/products",
        params={"component_type": "procesadores", "brand": "Intel", "limit": 10}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"Total procesadores Intel: {data['total']}")
        for i, p in enumerate(data['products'][:10], 1):
            print(f"  {i}. {p['name'][:65]} - ${p['price_usd']}")

def test_sercoplus():
    """Prueba endpoints de SercoPlus"""
    print_section("SERCOPLUS - Productos")
    
    response = requests.get(f"{BASE_URL}/api/stores/sercoplus/products?limit=5")
    if response.status_code == 200:
        data = response.json()
        print(f"Total productos: {data['total']}")
        print(f"Mostrando: {data['count']}/{data['total']}")
        print("\nPrimeros 5 productos:")
        for i, p in enumerate(data['products'][:5], 1):
            print(f"  {i}. {p['name'][:60]}")
            print(f"     Precio: ${p['price_usd']} | Stock: {p['stock']} | Marca: {p.get('brand', 'N/A')}")
    else:
        print(f"❌ Error: {response.status_code}")

def test_store_stats():
    """Prueba estadísticas de tiendas"""
    print_section("ESTADÍSTICAS POR TIENDA")
    
    stores = ['memorykings', 'sercoplus']
    
    for store in stores:
        response = requests.get(f"{BASE_URL}/api/stores/{store}/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 {data['store'].upper()}")
            print(f"   Total productos: {data['total_products']}")
            print(f"   Precio promedio: ${data['avg_price_usd']:.2f}")
            print(f"   Última actualización: {data.get('last_update', 'N/A')}")
            print(f"   Categorías:")
            for cat, count in data['categories'].items():
                print(f"      - {cat}: {count} productos")

def test_compare_stores():
    """Prueba comparación entre tiendas"""
    print_section("COMPARACIÓN ENTRE TODAS LAS TIENDAS")
    
    response = requests.get(f"{BASE_URL}/api/stores/compare-all")
    if response.status_code == 200:
        data = response.json()
        print(f"Timestamp: {data['timestamp']}\n")
        
        for store_name, store_data in data['stores'].items():
            if 'error' in store_data:
                print(f"❌ {store_name.upper()}: {store_data['error']}")
            else:
                print(f"✅ {store_name.upper()}: {store_data['total_products']} productos")
                if 'categories' in store_data:
                    for cat, count in list(store_data['categories'].items())[:3]:
                        print(f"   - {cat}: {count}")

def test_search():
    """Prueba búsqueda en todas las tiendas"""
    print_section("BÚSQUEDA: 'Core i5'")
    
    response = requests.get(f"{BASE_URL}/api/search", params={"query": "Core i5", "limit": 5})
    if response.status_code == 200:
        data = response.json()
        print(f"Resultados encontrados: {data['count']}")
        print("\nProductos:")
        for i, p in enumerate(data['products'], 1):
            print(f"  {i}. [{p['store'].upper()}] {p['name'][:55]}")
            print(f"     ${p['price_usd']} - Stock: {p['stock']}")

def test_mobile_endpoints():
    """Prueba endpoints móviles"""
    print_section("ENDPOINTS MÓVILES")
    
    # Latest
    print("📱 Últimos productos:")
    response = requests.get(f"{BASE_URL}/api/mobile/latest?limit=3")
    if response.status_code == 200:
        data = response.json()
        for i, p in enumerate(data['products'], 1):
            print(f"  {i}. [{p['store']}] {p['name'][:50]}")
            print(f"     ${p['price_usd']} - {p['type']}")
    
    # Best deals
    print("\n💰 Mejores ofertas:")
    response = requests.get(f"{BASE_URL}/api/mobile/best-deals?limit=3")
    if response.status_code == 200:
        data = response.json()
        for i, deal in enumerate(data['deals'], 1):
            print(f"  {i}. [{deal['store']}] {deal['name'][:50]}")
            print(f"     ${deal['price_usd']} - Disponible en {deal['stores_available']} tienda(s)")

def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*80)
    print("🧪 PRUEBA DE ENDPOINTS DE API - POR TIENDA")
    print("="*80)
    
    try:
        # Verificar que la API esté corriendo
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code != 200:
            print("❌ La API no está respondiendo. Ejecuta: python main.py")
            return
        
        print("✅ API conectada correctamente\n")
        
        # Ejecutar pruebas
        test_memorykings()
        test_sercoplus()
        test_store_stats()
        test_compare_stores()
        test_search()
        test_mobile_endpoints()
        
        print("\n" + "="*80)
        print("✅ PRUEBAS COMPLETADAS")
        print("="*80)
        print("\n📖 Documentación completa: http://localhost:8000/docs")
        print("📝 Guía de endpoints: Ver API_STORES_GUIDE.md\n")
        
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar a la API")
        print("   Asegúrate de que la API esté corriendo:")
        print("   python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
