"""
Configuración centralizada para todos los scrapers
"""
import os
from pathlib import Path

# Rutas base
BASE_DIR = Path(__file__).parent
SCRAPERS_DIR = BASE_DIR / 'scrapers'

# Configuración de scrapers
SCRAPERS_CONFIG = {
    'memorykings': {
        'enabled': True,
        'dir': SCRAPERS_DIR / 'memorykings',
        'output': 'products.json',
        'max_listados': 20,
        'max_products_per_listado': 30,
        'rate_limit': 0.5,  # segundos entre productos
    },
    'sercoplus': {
        'enabled': True,
        'dir': SCRAPERS_DIR / 'sercoplus',
        'output': 'products.json',
        'use_selenium': True,
        'rate_limit': 1.0,
    },
    'pcimpacto': {
        'enabled': False,  # Por implementar
        'dir': SCRAPERS_DIR / 'pcimpacto',
        'output': 'products.json',
    }
}

# Configuración de base de datos
DATABASE_CONFIG = {
    'path': BASE_DIR / 'pc_prices.db',
    'backup_dir': BASE_DIR / 'backups',
}

# Configuración de API
API_CONFIG = {
    'host': '0.0.0.0',
    'port': 8000,
    'debug': True,
}

# Categorías estándar (para normalización)
STANDARD_CATEGORIES = {
    'procesadores': ['procesadores', 'processors', 'cpu'],
    'tarjetas-video': ['tarjetas-video', 'gpu', 'graphics', 'tarjetas-graficas'],
    'memorias-ram': ['memorias-ram', 'ram', 'memory'],
    'almacenamiento': ['almacenamiento', 'ssd', 'hdd', 'storage', 'discos'],
    'placas-madre': ['placas-madre', 'motherboard', 'mainboard'],
}

# Marcas conocidas
KNOWN_BRANDS = {
    'procesadores': ['AMD', 'Intel'],
    'tarjetas-video': ['NVIDIA', 'AMD', 'Intel Arc', 'ASUS', 'MSI', 'Gigabyte', 'EVGA'],
    'memorias-ram': ['Kingston', 'Corsair', 'G.Skill', 'Crucial', 'Team Group', 'Patriot'],
    'almacenamiento': ['Samsung', 'Western Digital', 'WD', 'Seagate', 'Kingston', 'Crucial', 'Corsair'],
    'placas-madre': ['ASUS', 'MSI', 'Gigabyte', 'ASRock', 'EVGA'],
}

def get_scraper_config(store_name: str) -> dict:
    """Obtiene la configuración de un scraper específico"""
    return SCRAPERS_CONFIG.get(store_name, {})

def get_enabled_scrapers() -> list:
    """Obtiene lista de scrapers habilitados"""
    return [name for name, config in SCRAPERS_CONFIG.items() if config.get('enabled', False)]

def get_output_path(store_name: str) -> Path:
    """Obtiene la ruta completa del archivo de salida de un scraper"""
    config = get_scraper_config(store_name)
    if config:
        return config['dir'] / config.get('output', 'products.json')
    return None
