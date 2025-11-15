"""
Utility functions for Price Tracker
Store detection, price calculations, etc.

Author: HellSpawn
"""
from urllib.parse import urlparse
from typing import Optional, Dict


def detectar_tienda(url: str) -> Optional[str]:
    """
    Detectar la tienda desde la URL del producto
    
    Args:
        url: URL del producto
    
    Returns:
        str: Nombre de la tienda o None si no se reconoce
    """
    try:
        domain = urlparse(url).netloc.lower()
        
        # Mapeo de dominios a nombres de tiendas
        tiendas = {
            'amazon': ['amazon.com', 'amazon.com.mx', 'amazon.es', 'amazon.co.uk'],
            'mercadolibre': ['mercadolibre.com.mx', 'mercadolibre.com', 'mercadolibre.com.ar', 'mercadolibre.cl'],
            'ebay': ['ebay.com', 'ebay.com.mx', 'ebay.es'],
            'walmart': ['walmart.com', 'walmart.com.mx'],
            'bestbuy': ['bestbuy.com', 'bestbuy.com.mx'],
            'aliexpress': ['aliexpress.com', 'es.aliexpress.com'],
            'liverpool': ['liverpool.com.mx'],
            'claroshop': ['claroshop.com'],
            'coppel': ['coppel.com'],
            'elektra': ['elektra.com.mx'],
            'sears': ['sears.com.mx'],
            'costco': ['costco.com.mx', 'costco.com'],
            'homedepot': ['homedepot.com.mx', 'homedepot.com'],
        }
        
        for tienda, dominios in tiendas.items():
            if any(dominio in domain for dominio in dominios):
                return tienda
        
        # Si no se reconoce, devolver el dominio principal
        return domain.replace('www.', '').split('.')[0]
    
    except Exception as e:
        print(f"Error al detectar tienda: {e}")
        return None


def calcular_ahorro_porcentual(precio_actual: float, precio_maximo: float) -> Optional[float]:
    """
    Calcular el porcentaje de ahorro comparando precio actual vs precio máximo
    
    Args:
        precio_actual: Precio actual del producto
        precio_maximo: Precio máximo histórico
    
    Returns:
        float: Porcentaje de ahorro (ej: 15.5) o None si no se puede calcular
    """
    try:
        if not precio_actual or not precio_maximo or precio_maximo == 0:
            return None
        
        if precio_actual >= precio_maximo:
            return 0.0
        
        ahorro = ((precio_maximo - precio_actual) / precio_maximo) * 100
        return round(ahorro, 1)  # Redondear a 1 decimal
    
    except Exception as e:
        print(f"Error al calcular ahorro: {e}")
        return None


def get_store_icon_info(tienda: str) -> Dict[str, str]:
    """
    Obtener información de icono/color para una tienda
    
    Args:
        tienda: Nombre de la tienda
    
    Returns:
        dict: Información con color y emoji
    """
    store_info = {
        'amazon': {'color': '#FF9900', 'emoji': '📦', 'name': 'Amazon'},
        'mercadolibre': {'color': '#FFE600', 'emoji': '🛒', 'name': 'MercadoLibre'},
        'ebay': {'color': '#E53238', 'emoji': '🏷️', 'name': 'eBay'},
        'walmart': {'color': '#0071CE', 'emoji': '🏪', 'name': 'Walmart'},
        'bestbuy': {'color': '#0046BE', 'emoji': '🔌', 'name': 'Best Buy'},
        'aliexpress': {'color': '#E62E04', 'emoji': '🛍️', 'name': 'AliExpress'},
        'liverpool': {'color': '#BE1E2D', 'emoji': '🏬', 'name': 'Liverpool'},
        'claroshop': {'color': '#E00C00', 'emoji': '🛒', 'name': 'Claroshop'},
        'coppel': {'color': '#00447C', 'emoji': '🏪', 'name': 'Coppel'},
        'elektra': {'color': '#003087', 'emoji': '⚡', 'name': 'Elektra'},
        'sears': {'color': '#008CBA', 'emoji': '🏬', 'name': 'Sears'},
        'costco': {'color': '#0057A0', 'emoji': '🏪', 'name': 'Costco'},
        'homedepot': {'color': '#F96302', 'emoji': '🔨', 'name': 'Home Depot'},
    }
    
    return store_info.get(tienda.lower(), {
        'color': '#6B7280',
        'emoji': '🛒',
        'name': tienda.title()
    })
