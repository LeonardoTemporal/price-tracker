"""
Módulo de scraping para el Price Tracker.
Extrae precios de diferentes sitios web.

Author: HellSpawn
"""
import requests
from bs4 import BeautifulSoup
import re
from typing import Optional, Dict
import time
from urllib.parse import urlparse


class PriceScraper:
    """Clase para realizar scraping de precios en diferentes sitios web."""
    
    def __init__(self):
        """Inicializa el scraper con headers para simular un navegador."""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        }
        
        # Configuraciones específicas por dominio
        self.domain_configs = {
            'amazon': {
                'selectors': [
                    {'class': 'a-price-whole'},
                    {'id': 'priceblock_ourprice'},
                    {'id': 'priceblock_dealprice'},
                    {'class': 'a-offscreen'},
                ],
                'clean_pattern': r'[^\d,.]'
            },
            'mercadolibre': {
                'selectors': [
                    {'class': 'andes-money-amount__fraction'},
                    {'class': 'price-tag-fraction'},
                    {'class': 'ui-pdp-price__second-line__main-price'},
                    {'class': 'price-tag-amount'},
                    {'attrs': {'data-testid': 'price-part'}},
                    {'class': 'ui-pdp-price__part'},
                ],
                'clean_pattern': r'[^\d,.]'
            },
            'ebay': {
                'selectors': [
                    {'class': 'x-price-primary'},
                    {'id': 'prcIsum'},
                ],
                'clean_pattern': r'[^\d,.]'
            },
        }
    
    def get_price(self, url: str) -> Optional[float]:
        """
        Extrae el precio de una URL.
        
        Args:
            url: URL de la página del producto
        
        Returns:
            Precio como float o None si no se pudo extraer
        """
        try:
            print(f"🔍 Intentando extraer precio de: {url}")
            
            # Realiza la petición HTTP
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            print(f"✓ Respuesta HTTP {response.status_code}")
            
            # Parsea el HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Intenta extraer el precio usando configuraciones específicas del dominio
            domain = self._get_domain(url)
            print(f"🌐 Dominio detectado: {domain}")
            
            precio = self._extract_price_by_domain(soup, domain)
            
            # Si no funcionó, intenta métodos genéricos
            if precio is None:
                print("⚠️  Selectores de dominio fallaron, intentando métodos genéricos...")
                precio = self._extract_price_generic(soup)
            
            if precio:
                print(f"💰 Precio encontrado: ${precio}")
            else:
                print("❌ No se pudo extraer el precio")
                # Guardar HTML para debug
                print(f"📄 Primeros 500 caracteres del HTML:")
                print(soup.get_text()[:500])
            
            return precio
            
        except requests.RequestException as e:
            print(f"Error al acceder a la URL {url}: {e}")
            return None
        except Exception as e:
            print(f"Error inesperado al procesar {url}: {e}")
            return None
    
    def _get_domain(self, url: str) -> str:
        """
        Extrae el dominio principal de una URL.
        
        Args:
            url: URL completa
        
        Returns:
            Dominio principal (ej: 'amazon', 'mercadolibre')
        """
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Extrae el dominio principal
        for key in self.domain_configs.keys():
            if key in domain:
                return key
        
        return 'generic'
    
    def _extract_price_by_domain(self, soup: BeautifulSoup, domain: str) -> Optional[float]:
        """
        Extrae el precio usando configuraciones específicas del dominio.
        
        Args:
            soup: Objeto BeautifulSoup con el HTML parseado
            domain: Dominio del sitio web
        
        Returns:
            Precio como float o None
        """
        if domain not in self.domain_configs:
            return None
        
        config = self.domain_configs[domain]
        
        # Intenta cada selector configurado
        for selector in config['selectors']:
            element = None
            
            if 'class' in selector:
                element = soup.find(class_=selector['class'])
            elif 'id' in selector:
                element = soup.find(id=selector['id'])
            elif 'attrs' in selector:
                element = soup.find(attrs=selector['attrs'])
            
            if element:
                precio_texto = element.get_text().strip()
                precio = self._clean_price(precio_texto, config['clean_pattern'])
                if precio is not None:
                    print(f"✓ Precio encontrado con selector {selector}: {precio}")
                    return precio
        
        return None
    
    def _extract_price_generic(self, soup: BeautifulSoup) -> Optional[float]:
        """
        Intenta extraer el precio usando patrones genéricos.
        
        Args:
            soup: Objeto BeautifulSoup con el HTML parseado
        
        Returns:
            Precio como float o None
        """
        # Busca patrones comunes de precio en el HTML
        price_patterns = [
            r'\$\s*(\d+[.,]\d+)',
            r'(\d+[.,]\d+)\s*€',
            r'precio[:\s]+\$?\s*(\d+[.,]\d+)',
            r'price[:\s]+\$?\s*(\d+[.,]\d+)',
        ]
        
        text = soup.get_text()
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                precio_texto = matches[0]
                precio = self._clean_price(precio_texto)
                if precio is not None and precio > 0:
                    return precio
        
        return None
    
    def _clean_price(self, precio_texto: str, pattern: str = r'[^\d,.]') -> Optional[float]:
        """
        Limpia y convierte un texto de precio a float.
        
        Args:
            precio_texto: Texto con el precio
            pattern: Patrón regex para limpiar caracteres no deseados
        
        Returns:
            Precio como float o None si no se pudo convertir
        """
        try:
            # Elimina caracteres no deseados
            precio_limpio = re.sub(pattern, '', precio_texto)
            
            # Maneja diferentes formatos de separadores decimales
            # Reemplaza coma por punto si es el último separador
            if ',' in precio_limpio and '.' in precio_limpio:
                # Formato: 1.234,56 -> 1234.56
                precio_limpio = precio_limpio.replace('.', '').replace(',', '.')
            elif ',' in precio_limpio:
                # Verifica si es decimal o separador de miles
                partes = precio_limpio.split(',')
                if len(partes[-1]) <= 2:  # Es decimal
                    precio_limpio = precio_limpio.replace(',', '.')
                else:  # Es separador de miles
                    precio_limpio = precio_limpio.replace(',', '')
            
            precio = float(precio_limpio)
            return precio if precio > 0 else None
            
        except (ValueError, AttributeError):
            return None
    
    def test_url(self, url: str) -> Dict:
        """
        Prueba una URL y retorna información de diagnóstico.
        
        Args:
            url: URL a probar
        
        Returns:
            Diccionario con información de la prueba
        """
        resultado = {
            'url': url,
            'accesible': False,
            'precio': None,
            'error': None,
            'domain': self._get_domain(url)
        }
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            resultado['accesible'] = response.status_code == 200
            
            if resultado['accesible']:
                soup = BeautifulSoup(response.content, 'html.parser')
                precio = self.get_price(url)
                resultado['precio'] = precio
                
                if precio is None:
                    resultado['error'] = "No se pudo extraer el precio del HTML"
            else:
                resultado['error'] = f"Código de estado: {response.status_code}"
                
        except requests.RequestException as e:
            resultado['error'] = str(e)
        except Exception as e:
            resultado['error'] = f"Error inesperado: {str(e)}"
        
        return resultado


# Función auxiliar para uso rápido
def get_price(url: str) -> Optional[float]:
    """
    Función auxiliar para extraer un precio de una URL.
    
    Args:
        url: URL de la página del producto
    
    Returns:
        Precio como float o None
    """
    scraper = PriceScraper()
    return scraper.get_price(url)
