"""
Scraper mejorado usando Playwright para evitar detección anti-bot
Renderiza JavaScript como un navegador real

Author: HellSpawn
"""
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
import re
from typing import Optional
import asyncio


class PlaywrightScraper:
    """Scraper que usa Playwright para renderizar JavaScript"""
    
    def __init__(self):
        """Inicializa el scraper con Playwright"""
        self.playwright = None
        self.browser = None
        self.context = None
        
    async def __aenter__(self):
        """Context manager entry"""
        self.playwright = await async_playwright().start()
        # Lanzar navegador en modo headless
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
            ]
        )
        # Crear contexto con configuración de navegador real
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='es-MX',
            timezone_id='America/Mexico_City',
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def get_price(self, url: str) -> Optional[float]:
        """
        Extrae el precio de una URL usando Playwright
        
        Args:
            url: URL de la página del producto
        
        Returns:
            Precio como float o None si no se pudo extraer
        """
        try:
            print(f"🌐 [Playwright] Navegando a: {url}")
            
            page = await self.context.new_page()
            
            # Navegar a la URL
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            print(f"✓ Página cargada: {await page.title()}")
            
            # Esperar a que el precio se cargue
            try:
                # Esperar por selectores comunes de precio en MercadoLibre
                await page.wait_for_selector(
                    '.andes-money-amount__fraction, .price-tag-fraction, .ui-pdp-price__part',
                    timeout=10000
                )
                print("✓ Elemento de precio encontrado")
            except PlaywrightTimeout:
                print("⚠️  Timeout esperando elemento de precio")
            
            # Esperar un momento adicional para que todo cargue
            await asyncio.sleep(2)
            
            # Obtener el HTML renderizado
            html = await page.content()
            
            # Cerrar la página
            await page.close()
            
            # Parsear con BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Intentar extraer el precio
            precio = self._extract_price_mercadolibre(soup)
            
            if precio:
                print(f"💰 Precio encontrado: ${precio}")
            else:
                print("❌ No se pudo extraer el precio")
                # Debug: mostrar primeros caracteres
                text = soup.get_text()[:500]
                print(f"📄 Primeros 500 caracteres: {text}")
            
            return precio
            
        except Exception as e:
            print(f"❌ Error en Playwright scraper: {e}")
            import traceback
            print(traceback.format_exc())
            return None
    
    def _extract_price_mercadolibre(self, soup: BeautifulSoup) -> Optional[float]:
        """
        Extrae el precio de MercadoLibre del HTML renderizado
        
        Args:
            soup: BeautifulSoup object
        
        Returns:
            Precio como float o None
        """
        # Lista de selectores para probar
        selectors = [
            {'class': 'andes-money-amount__fraction'},
            {'class': 'price-tag-fraction'},
            {'class': 'ui-pdp-price__second-line__main-price'},
            {'class': 'price-tag-amount'},
            {'class': 'ui-pdp-price__part'},
            {'attrs': {'data-testid': 'price-part'}},
        ]
        
        for selector in selectors:
            element = None
            
            if 'class' in selector:
                element = soup.find(class_=selector['class'])
            elif 'attrs' in selector:
                element = soup.find(attrs=selector['attrs'])
            
            if element:
                precio_texto = element.get_text().strip()
                precio = self._clean_price(precio_texto)
                if precio and precio > 0:
                    print(f"✓ Precio extraído con selector {selector}: ${precio}")
                    return precio
        
        # Intento genérico con regex
        text = soup.get_text()
        patterns = [
            r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d{1,3}(?:,\d{3})*)\s*pesos',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                precio_texto = matches[0]
                precio = self._clean_price(precio_texto)
                if precio and precio > 0:
                    print(f"✓ Precio extraído con regex: ${precio}")
                    return precio
        
        return None
    
    def _clean_price(self, precio_texto: str) -> Optional[float]:
        """
        Limpia y convierte texto de precio a float
        
        Args:
            precio_texto: Texto con el precio
        
        Returns:
            Precio como float o None
        """
        try:
            # Eliminar todo excepto números, comas y puntos
            precio_limpio = re.sub(r'[^\d,.]', '', precio_texto)
            
            # Manejar separadores
            if ',' in precio_limpio and '.' in precio_limpio:
                # Formato: 1.234,56 o 1,234.56
                if precio_limpio.index(',') < precio_limpio.index('.'):
                    # 1,234.56
                    precio_limpio = precio_limpio.replace(',', '')
                else:
                    # 1.234,56
                    precio_limpio = precio_limpio.replace('.', '').replace(',', '.')
            elif ',' in precio_limpio:
                # Verificar si es decimal o separador de miles
                partes = precio_limpio.split(',')
                if len(partes[-1]) <= 2:
                    precio_limpio = precio_limpio.replace(',', '.')
                else:
                    precio_limpio = precio_limpio.replace(',', '')
            
            precio = float(precio_limpio)
            return precio if precio > 0 else None
            
        except (ValueError, AttributeError):
            return None


# Función auxiliar para uso rápido
async def get_price(url: str) -> Optional[float]:
    """
    Función auxiliar para extraer precio usando Playwright
    
    Args:
        url: URL de la página del producto
    
    Returns:
        Precio como float o None
    """
    async with PlaywrightScraper() as scraper:
        return await scraper.get_price(url)
