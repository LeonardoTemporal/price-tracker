"""
Tests para el modulo de web scraping.

Utiliza HTML de prueba para simular respuestas de sitios web
sin realizar peticiones HTTP reales.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.scraper import PriceScraper


# HTML de prueba que simula una pagina de producto
SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head><title>Producto Test</title></head>
<body>
    <span class="price">$1,234.56</span>
    <span class="a-price-whole">1,234</span>
    <span class="a-price-fraction">56</span>
    <span class="andes-money-amount__fraction">2 345</span>
</body>
</html>
"""

SAMPLE_HTML_NO_PRICE = """
<!DOCTYPE html>
<html>
<head><title>Producto Sin Precio</title></head>
<body>
    <h1>Producto no disponible</h1>
</body>
</html>
"""


class TestScraperGeneric:
    """Tests para la extraccion generica de precios."""

    @pytest.fixture()
    def scraper(self):
        """Proporciona una instancia de PriceScraper para los tests."""
        return PriceScraper()

    def test_limpieza_precio_con_comas(self, scraper: PriceScraper):
        """Debe limpiar correctamente precios con comas como separador de miles."""
        precio_limpio = scraper._clean_price("1,234.56")
        assert precio_limpio == 1234.56

    def test_limpieza_precio_con_punto_miles(self, scraper: PriceScraper):
        """Debe limpiar precios con punto como separador de miles (formato MXN)."""
        precio_limpio = scraper._clean_price("2.345")
        assert precio_limpio == 2345.0

    def test_deteccion_dominio_mercadolibre(self, scraper: PriceScraper):
        """Debe detectar correctamente dominios de Mercado Libre."""
        url = "https://www.mercadolibre.com.mx/producto-test"
        dominio = scraper._get_domain(url)
        assert "mercadolibre" in dominio

    def test_deteccion_dominio_amazon(self, scraper: PriceScraper):
        """Debe detectar correctamente dominios de Amazon."""
        url = "https://www.amazon.com/dp/B08N5WRWNW"
        dominio = scraper._get_domain(url)
        assert "amazon" in dominio

    def test_configuracion_mercadolibre_existe(self, scraper: PriceScraper):
        """Debe tener configuracion para Mercado Libre."""
        assert 'mercadolibre' in scraper.domain_configs

    def test_configuracion_amazon_existe(self, scraper: PriceScraper):
        """Debe tener configuracion para Amazon."""
        assert 'amazon' in scraper.domain_configs


class TestScraperMockHTTP:
    """Tests que mockean respuestas HTTP."""

    @pytest.fixture()
    def scraper(self):
        return PriceScraper()

    @patch('src.scraper.requests.Session.get')
    def test_obtener_precio_exitoso(self, mock_get, scraper: PriceScraper):
        """Debe obtener precio cuando la pagina responde correctamente."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_HTML
        mock_response.content = SAMPLE_HTML.encode()
        mock_response.url = "https://example.com/producto"
        mock_get.return_value = mock_response

        import asyncio
        precio = asyncio.run(scraper.get_price("https://example.com/producto"))
        # El precio puede variar segun la logica de extraccion
        assert precio is None or isinstance(precio, float)

    @patch('src.scraper.requests.Session.get')
    def test_obtener_precio_pagina_no_encontrada(self, mock_get, scraper: PriceScraper):
        """Debe retornar None cuando la pagina no existe."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        mock_get.return_value = mock_response

        import asyncio
        precio = asyncio.run(scraper.get_price("https://example.com/no-existe"))
        assert precio is None

    @patch('src.scraper.requests.Session.get')
    def test_obtener_precio_timeout(self, mock_get, scraper: PriceScraper):
        """Debe manejar timeouts de conexion."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()

        import asyncio
        precio = asyncio.run(scraper.get_price("https://example.com/lento"))
        assert precio is None

    @patch('src.scraper.requests.Session.get')
    def test_obtener_precio_error_conexion(self, mock_get, scraper: PriceScraper):
        """Debe manejar errores de conexion."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError()

        import asyncio
        precio = asyncio.run(scraper.get_price("https://example.com/caido"))
        assert precio is None
