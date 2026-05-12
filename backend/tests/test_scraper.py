"""
Tests para el modulo de web scraping.

Utiliza HTML de prueba para simular respuestas de sitios web
sin realizar peticiones HTTP reales.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.scraper import Scraper


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
        """Proporciona una instancia de Scraper para los tests."""
        return Scraper()

    def test_extraer_precio_con_formato_dolar_coma(self, scraper: Scraper):
        """Debe extraer precios con formato $1,234.56."""
        precio = scraper._extract_price_with_pattern(SAMPLE_HTML, r'\$([\d,]+\.\d{2})')
        assert precio == 1234.56

    def test_extraer_precio_sin_simbolo(self, scraper: Scraper):
        """Debe extraer precios sin simbolo de moneda."""
        precio = scraper._extract_price_with_pattern(SAMPLE_HTML, r'([\d,]+\.\d{2})')
        assert precio is not None

    def test_extraer_precio_html_sin_precio(self, scraper: Scraper):
        """Debe retornar None cuando no encuentra precio."""
        precio = scraper._extract_price_with_pattern(SAMPLE_HTML_NO_PRICE, r'\$([\d,]+\.\d{2})')
        assert precio is None

    def test_limpieza_precio_con_comas(self, scraper: Scraper):
        """Debe limpiar correctamente precios con comas como separador de miles."""
        precio_limpio = scraper._clean_price("1,234.56")
        assert precio_limpio == 1234.56

    def test_limpieza_precio_con_punto_miles(self, scraper: Scraper):
        """Debe limpiar precios con punto como separador de miles (formato MXN)."""
        # Simulamos formato 2.345,67
        precio_limpio = scraper._clean_price("2.345")
        assert precio_limpio == 2345.0

    def test_deteccion_dominio_mercadolibre(self, scraper: Scraper):
        """Debe detectar correctamente dominios de Mercado Libre."""
        url = "https://www.mercadolibre.com.mx/producto-test"
        dominio = scraper._get_domain(url)
        assert "mercadolibre" in dominio

    def test_deteccion_dominio_amazon(self, scraper: Scraper):
        """Debe detectar correctamente dominios de Amazon."""
        url = "https://www.amazon.com/dp/B08N5WRWNW"
        dominio = scraper._get_domain(url)
        assert "amazon" in dominio


class TestScraperMockHTTP:
    """Tests que mockean respuestas HTTP."""

    @pytest.fixture()
    def scraper(self):
        return Scraper()

    @patch('src.scraper.requests.get')
    def test_obtener_precio_exitoso(self, mock_get, scraper: Scraper):
        """Debe obtener precio cuando la pagina responde correctamente."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_HTML
        mock_get.return_value = mock_response

        precio = scraper.get_price("https://example.com/producto")
        assert precio is not None
        assert isinstance(precio, float)

    @patch('src.scraper.requests.get')
    def test_obtener_precio_pagina_no_encontrada(self, mock_get, scraper: Scraper):
        """Debe retornar None cuando la pagina no existe."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        precio = scraper.get_price("https://example.com/no-existe")
        assert precio is None

    @patch('src.scraper.requests.get')
    def test_obtener_precio_timeout(self, mock_get, scraper: Scraper):
        """Debe manejar timeouts de conexion."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()

        precio = scraper.get_price("https://example.com/lento")
        assert precio is None

    @patch('src.scraper.requests.get')
    def test_obtener_precio_error_conexion(self, mock_get, scraper: Scraper):
        """Debe manejar errores de conexion."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError()

        precio = scraper.get_price("https://example.com/caido")
        assert precio is None


class TestScraperDomainConfigs:
    """Tests para configuraciones especificas por dominio."""

    @pytest.fixture()
    def scraper(self):
        return Scraper()

    def test_configuracion_mercadolibre_existe(self, scraper: Scraper):
        """Debe tener configuracion para Mercado Libre."""
        assert 'mercadolibre' in scraper.domain_configs or any(
            'mercadolibre' in key for key in scraper.domain_configs.keys()
        )

    def test_configuracion_amazon_existe(self, scraper: Scraper):
        """Debe tener configuracion para Amazon."""
        assert 'amazon' in scraper.domain_configs or any(
            'amazon' in key for key in scraper.domain_configs.keys()
        )
