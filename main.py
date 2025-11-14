"""
PC Component Price Scraper API
FastAPI application for scraping and comparing PC component prices
Optimized for mobile app consumption (iOS)
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import uvicorn
import logging

from database import Database
from scrapers import SercoPlusScraper, PCImpactoScraper, ComputerShopScraper
# from product_matcher import ProductMatcher  # Módulo no utilizado actualmente
# from scheduler import ScrapingScheduler, STORE_URLS  # Comentado temporalmente
from config import config

app = FastAPI(
    title="PC Price Scraper API",
    description="API para comparar precios de componentes de PC",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize database, scrapers, and utilities
db = Database(config.DATABASE_PATH)
# matcher = ProductMatcher(db)  # No utilizado actualmente
# scheduler = ScrapingScheduler(db)  # Comentado temporalmente

# Initialize store-specific scrapers
scrapers = {
    'SercoPlus': SercoPlusScraper(),
    'PCImpacto': PCImpactoScraper(),
    'ComputerShop': ComputerShopScraper()
}

# Pydantic models
class ScrapeRequest(BaseModel):
    url: str = Field(..., description="URL de la página a scrapear")
    store_name: str = Field(..., description="Nombre de la tienda")

class ProductCreate(BaseModel):
    name: str
    price: float
    currency: str = "USD"
    url: str
    store_name: str
    component_type: Optional[str] = None
    image_url: Optional[str] = None
    brand: Optional[str] = None
    stock_status: Optional[str] = "available"
    sku: Optional[str] = None
    
class ComponentFilter(BaseModel):
    component_type: Optional[str] = None
    brand: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    store: Optional[str] = None

class PriceComparisonResponse(BaseModel):
    product_name: str
    prices: List[Dict]
    lowest_price: Dict
    highest_price: Dict
    price_difference: float


@app.on_event("startup")
async def startup_event():
    """Initialize database and scheduler on startup"""
    db.init_db()
    logger.info("✅ Database initialized")
    
    # Start scheduler if enabled
    # if config.ENABLE_AUTO_SCRAPING:
    #     scheduler.start_scheduler()
    #     logger.info("✅ Scheduler started")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    # if scheduler.is_running:
    #     scheduler.stop_scheduler()
    #     logger.info("⏹️ Scheduler stopped")
    pass

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PC Component Price Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "scrape": "/api/scrape",
            "products": "/api/products",
            "compare": "/api/compare/{product_name}",
            "stores": "/api/stores",
            "stats": "/api/stats"
        }
    }

@app.get("/favicon.ico")
async def favicon():
    """Favicon endpoint to prevent 404 errors"""
    return {"status": "no favicon"}

@app.post("/api/scrape")
async def scrape_store(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """
    Scrapea productos de una URL específica
    
    - **url**: URL de la página a scrapear
    - **store_name**: Nombre de la tienda (SercoPlus, PCImpacto, o ComputerShop)
    """
    try:
        # Get appropriate scraper
        scraper = scrapers.get(request.store_name)
        
        if not scraper:
            raise HTTPException(
                status_code=400, 
                detail=f"Tienda no soportada: {request.store_name}. Use: SercoPlus, PCImpacto, o ComputerShop"
            )
        
        # Scrape products
        logger.info(f"Scraping {request.store_name}: {request.url}")
        products = scraper.scrape_category_page(request.url)
        
        if not products:
            raise HTTPException(status_code=404, detail="No se encontraron productos")
        
        # Save to database
        saved_count = 0
        for product in products:
            if db.insert_product(product):
                saved_count += 1
        
        logger.info(f"Saved {saved_count}/{len(products)} products from {request.store_name}")
        
        return {
            "status": "success",
            "message": f"Se scrapearon {len(products)} productos",
            "saved": saved_count,
            "store": request.store_name,
            "url": request.url,
            "products": products[:5]  # Return first 5 as sample
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scraping {request.store_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al scrapear: {str(e)}")

@app.get("/api/products")
async def get_products(
    skip: int = 0,
    limit: int = 50,
    component_type: Optional[str] = None,
    brand: Optional[str] = None,
    store: Optional[str] = None
):
    """
    Obtiene lista de productos con filtros opcionales
    
    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Número máximo de registros a retornar
    - **component_type**: Filtrar por tipo de componente
    - **brand**: Filtrar por marca
    - **store**: Filtrar por tienda
    """
    filters = ComponentFilter(
        component_type=component_type,
        brand=brand,
        store=store
    )
    
    products = db.get_products(skip, limit, filters)
    total = db.count_products(filters)
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "count": len(products),
        "products": products
    }

@app.post("/api/products")
async def create_product(product: ProductCreate):
    """
    Crea un nuevo producto en la base de datos
    
    - **name**: Nombre del producto
    - **price**: Precio en USD
    - **url**: URL del producto
    - **store_name**: Nombre de la tienda
    """
    try:
        product_dict = {
            "name": product.name,
            "price": product.price,
            "currency": product.currency,
            "url": product.url,
            "store_name": product.store_name,
            "component_type": product.component_type,
            "image_url": product.image_url,
            "brand": product.brand,
            "stock_status": product.stock_status,
            "sku": product.sku
        }
        
        if db.insert_product(product_dict):
            return {"status": "success", "message": "Producto creado"}
        else:
            raise HTTPException(status_code=409, detail="Producto duplicado (URL ya existe)")
            
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{product_id}")
async def get_product(product_id: int):
    """Obtiene un producto específico por ID"""
    product = db.get_product_by_id(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return product

# Endpoint deshabilitado temporalmente - requiere ProductMatcher
# @app.get("/api/compare/{product_name}")
# async def compare_prices(product_name: str, component_type: Optional[str] = None):
#     """
#     Compara precios de un producto en diferentes tiendas (con matching inteligente)
#     
#     - **product_name**: Nombre del producto a comparar
#     - **component_type**: Tipo de componente (opcional, mejora precisión)
#     """
#     # Use smart matcher for better cross-store comparison
#     comparison = matcher.compare_product_prices(product_name, component_type)
#     
#     if not comparison:
#         raise HTTPException(
#             status_code=404, 
#             detail=f"No se encontraron productos similares para '{product_name}'"
#         )
#     
#     return comparison

@app.get("/api/search")
async def search_products(query: str, limit: int = 20):
    """
    Busca productos por nombre
    
    - **query**: Término de búsqueda
    - **limit**: Número máximo de resultados
    """
    products = db.search_products(query, limit)
    
    return {
        "query": query,
        "count": len(products),
        "products": products
    }

@app.get("/api/stores")
async def get_stores():
    """Obtiene lista de todas las tiendas registradas"""
    stores = db.get_all_stores()
    
    return {
        "total": len(stores),
        "stores": stores
    }

# ============= STORE-SPECIFIC ENDPOINTS =============

@app.get("/api/stores/sercoplus/products")
async def get_sercoplus_products(
    skip: int = 0,
    limit: int = 50,
    component_type: Optional[str] = None,
    brand: Optional[str] = None
):
    """
    Obtiene productos exclusivamente de SercoPlus
    
    - **skip**: Número de registros a saltar
    - **limit**: Número máximo de registros
    - **component_type**: procesadores, tarjetas-video, memorias-ram, etc.
    - **brand**: AMD, Intel, NVIDIA, etc.
    """
    filters = ComponentFilter(
        component_type=component_type,
        brand=brand,
        store='sercoplus'
    )
    
    products = db.get_products(skip, limit, filters)
    total = db.count_products(filters)
    
    return {
        "store": "sercoplus",
        "total": total,
        "skip": skip,
        "limit": limit,
        "count": len(products),
        "products": products
    }

@app.get("/api/stores/pcimpacto/products")
async def get_pcimpacto_products(
    skip: int = 0,
    limit: int = 50,
    component_type: Optional[str] = None,
    brand: Optional[str] = None
):
    """
    Obtiene productos exclusivamente de PCImpacto
    
    - **skip**: Número de registros a saltar
    - **limit**: Número máximo de registros
    - **component_type**: procesadores, tarjetas-video, memorias-ram, etc.
    - **brand**: AMD, Intel, NVIDIA, etc.
    """
    filters = ComponentFilter(
        component_type=component_type,
        brand=brand,
        store='pcimpacto'
    )
    
    products = db.get_products(skip, limit, filters)
    total = db.count_products(filters)
    
    return {
        "store": "pcimpacto",
        "total": total,
        "skip": skip,
        "limit": limit,
        "count": len(products),
        "products": products
    }

@app.get("/api/stores/cyccomputer/products")
async def get_cyccomputer_products(
    skip: int = 0,
    limit: int = 50,
    component_type: Optional[str] = None,
    brand: Optional[str] = None
):
    """
    Obtiene productos exclusivamente de CycComputer
    
    - **skip**: Número de registros a saltar
    - **limit**: Número máximo de registros
    - **component_type**: procesadores, tarjetas-video, memorias-ram, etc.
    - **brand**: AMD, Intel, NVIDIA, etc.
    """
    filters = ComponentFilter(
        component_type=component_type,
        brand=brand,
        store='cyccomputer'
    )
    
    products = db.get_products(skip, limit, filters)
    total = db.count_products(filters)
    
    return {
        "store": "cyccomputer",
        "total": total,
        "skip": skip,
        "limit": limit,
        "count": len(products),
        "products": products
    }

@app.get("/api/stores/computershop/products")
async def get_computershop_products(
    skip: int = 0,
    limit: int = 50,
    component_type: Optional[str] = None,
    brand: Optional[str] = None
):
    """
    Obtiene productos exclusivamente de ComputerShop Peru
    
    - **skip**: Número de registros a saltar
    - **limit**: Número máximo de registros
    - **component_type**: procesadores, tarjetas-video, memorias-ram, etc.
    - **brand**: AMD, Intel, NVIDIA, etc.
    """
    filters = ComponentFilter(
        component_type=component_type,
        brand=brand,
        store='computershop'
    )
    
    products = db.get_products(skip, limit, filters)
    total = db.count_products(filters)
    
    return {
        "store": "computershop",
        "total": total,
        "skip": skip,
        "limit": limit,
        "count": len(products),
        "products": products
    }

@app.get("/api/stores/{store_name}/stats")
async def get_store_stats(store_name: str):
    """
    Obtiene estadísticas de una tienda específica
    
    - **store_name**: sercoplus, pcimpacto, cyccomputer, o computershop
    """
    store_name = store_name.lower()
    
    if store_name not in ['sercoplus', 'pcimpacto', 'cyccomputer', 'computershop']:
        raise HTTPException(
            status_code=400,
            detail=f"Tienda no válida. Use: sercoplus, pcimpacto, cyccomputer, o computershop"
        )
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Total productos por categoría
    cursor.execute("""
        SELECT component_type, COUNT(*) as count
        FROM products
        WHERE store = ? AND is_active = 1
        GROUP BY component_type
    """, (store_name,))
    categories = {row['component_type']: row['count'] for row in cursor.fetchall()}
    
    # Total productos
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM products
        WHERE store = ? AND is_active = 1
    """, (store_name,))
    total = cursor.fetchone()['total']
    
    # Precio promedio
    cursor.execute("""
        SELECT AVG(price_usd) as avg_price
        FROM products
        WHERE store = ? AND is_active = 1 AND price_usd > 0
    """, (store_name,))
    avg_price = cursor.fetchone()['avg_price']
    
    # Última actualización
    cursor.execute("""
        SELECT MAX(last_scraped) as last_update
        FROM products
        WHERE store = ?
    """, (store_name,))
    last_update = cursor.fetchone()['last_update']
    
    conn.close()
    
    return {
        "store": store_name,
        "total_products": total,
        "categories": categories,
        "avg_price_usd": round(avg_price, 2) if avg_price else 0,
        "last_update": last_update
    }

@app.get("/api/stores/compare-all")
async def compare_all_stores():
    """
    Compara estadísticas de todas las tiendas
    """
    stores = ['sercoplus', 'pcimpacto', 'cyccomputer', 'computershop']
    comparison = {}
    
    for store in stores:
        try:
            store_data = await get_store_stats(store)
            comparison[store] = store_data
        except:
            comparison[store] = {"error": "No disponible"}
    
    return {
        "stores": comparison,
        "timestamp": datetime.now().isoformat()
    }@app.get("/api/stats")
async def get_statistics():
    """Obtiene estadísticas generales del sistema"""
    stats = db.get_statistics()
    
    return stats

@app.delete("/api/products/{product_id}")
async def delete_product(product_id: int):
    """Elimina un producto específico"""
    success = db.delete_product(product_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return {"status": "success", "message": f"Producto {product_id} eliminado"}

@app.get("/api/brands")
async def get_brands():
    """Obtiene lista de todas las marcas registradas"""
    brands = db.get_all_brands()
    
    return {
        "total": len(brands),
        "brands": brands
    }

@app.get("/api/types")
async def get_component_types():
    """Obtiene lista de todos los tipos de componentes"""
    types = db.get_all_types()
    
    return {
        "total": len(types),
        "types": types
    }


# ============= NEW ENDPOINTS FOR MOBILE & AUTOMATION =============

@app.post("/api/schedule/add")
# SCHEDULER DESHABILITADO - Funciones comentadas
# async def add_scheduled_task(
#     store_name: str = Query(..., description="Nombre de la tienda"),
#     url: str = Query(..., description="URL a scrapear"),
#     category: str = Query('', description="Categoría del producto"),
#     frequency_hours: int = Query(24, description="Frecuencia en horas")
# ):
#     """
#     Agrega una tarea programada de scraping
#     
#     - **store_name**: SercoPlus, MemoryKings, o PCImpacto
#     - **url**: URL de la categoría a scrapear
#     - **category**: Nombre de la categoría
#     - **frequency_hours**: Cada cuántas horas scrapear (default: 24)
#     """
#     if store_name not in scrapers:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Tienda no válida. Use: {', '.join(scrapers.keys())}"
#         )
#     
#     success = scheduler.add_scraping_task(store_name, url, category, frequency_hours)
#     
#     if not success:
#         raise HTTPException(status_code=500, detail="Error agregando tarea")
#     
#     return {
#         "status": "success",
#         "message": f"Tarea programada para {store_name}",
#         "frequency_hours": frequency_hours
#     }


# @app.get("/api/schedule/status")
# async def get_scheduler_status():
#     """Obtiene el estado del scheduler y tareas programadas"""
#     status = scheduler.get_schedule_status()
#     
#     return {
#         "status": "success",
#         "scheduler": status
#     }


# @app.get("/api/schedule/logs")
# async def get_scraping_logs(
#     limit: int = Query(50, description="Número de logs a retornar"),
#     store_name: Optional[str] = Query(None, description="Filtrar por tienda")
# ):
#     """Obtiene logs de ejecuciones de scraping"""
#     logs = scheduler.get_scraping_logs(limit, store_name)
#     
#     return {
#         "total": len(logs),
#         "logs": logs
#     }


# @app.post("/api/schedule/run-now")
# async def run_scheduled_tasks_now(background_tasks: BackgroundTasks):
#     """Ejecuta todas las tareas pendientes inmediatamente"""
#     background_tasks.add_task(scheduler.check_and_run_tasks)
#     
#     return {
#         "status": "success",
#         "message": "Tareas programadas ejecutándose en segundo plano"
#     }


@app.get("/api/mobile/latest")
async def get_latest_products_mobile(
    limit: int = Query(20, description="Productos a retornar"),
    component_type: Optional[str] = Query(None, description="Filtrar por tipo")
):
    """
    Endpoint optimizado para app móvil: últimos productos actualizados
    Incluye información mínima necesaria
    """
    filters = ComponentFilter(component_type=component_type) if component_type else None
    products = db.get_products(0, limit, filters)
    
    # Simplify for mobile
    mobile_products = []
    for p in products:
        mobile_products.append({
            "id": p["id"],
            "name": p["name"],
            "brand": p["brand"],
            "type": p["component_type"],
            "price_usd": p["price_usd"],
            "price_pen": p.get("price_local"),
            "stock": p["stock"],
            "store": p["store"],
            "url": p.get("source_url"),
            "updated": p.get("last_scraped")
        })
    
    return {
        "count": len(mobile_products),
        "products": mobile_products
    }


@app.get("/api/mobile/best-deals")
async def get_best_deals_mobile(
    component_type: Optional[str] = Query(None, description="Tipo de componente"),
    limit: int = Query(10, description="Número de ofertas")
):
    """
    Obtiene las mejores ofertas actuales (productos con mayor descuento entre tiendas)
    Optimizado para app móvil
    """
    # Get products with price history to find best deals
    # This is a simplified version - you could enhance with actual discount calculation
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT p.*, 
               (SELECT COUNT(*) FROM products p2 
                WHERE p2.normalized_name = p.normalized_name 
                AND p2.store != p.store) as store_count
        FROM products p
        WHERE is_active = 1
    """
    
    params = []
    if component_type:
        query += " AND component_type = ?"
        params.append(component_type)
    
    query += " ORDER BY price_usd ASC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    deals = []
    for p in products:
        deals.append({
            "id": p["id"],
            "name": p["name"],
            "brand": p["brand"],
            "price_usd": p["price_usd"],
            "price_pen": p.get("price_local"),
            "store": p["store"],
            "url": p.get("source_url"),
            "stores_available": p.get("store_count", 1)
        })
    
    return {
        "count": len(deals),
        "deals": deals
    }


@app.get("/api/mobile/compare-quick/{product_id}")
async def quick_compare_mobile(product_id: int):
    """
    Comparación rápida desde un producto específico
    Optimizado para app móvil
    """
    product = db.get_product_by_id(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Find matches (ProductMatcher no disponible actualmente)
    # matches = matcher.find_matches(product, threshold=0.7)
    matches = []  # Temporalmente vacío
    
    comparison = {
        "product": {
            "id": product["id"],
            "name": product["name"],
            "price_usd": product["price_usd"],
            "store": product["store"]
        },
        "alternatives": []
    }
    
    for match in matches[:5]:  # Top 5 matches
        alt = match['product']
        comparison["alternatives"].append({
            "id": alt["id"],
            "name": alt["name"],
            "price_usd": alt["price_usd"],
            "price_diff": alt["price_usd"] - product["price_usd"],
            "store": alt["store"],
            "url": alt.get("source_url"),
            "confidence": round(match['similarity'] * 100, 1)
        })
    
    return comparison


@app.get("/api/config")
async def get_configuration():
    """Obtiene la configuración actual del sistema"""
    return {
        "status": "success",
        "config": config.to_dict(),
        "stores": list(scrapers.keys()),
        # "predefined_urls": STORE_URLS  # Comentado - scheduler disabled
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint para monitoreo"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        # "scheduler_running": scheduler.is_running,  # Comentado - scheduler disabled
        "database": "connected"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.API_RELOAD
    )
