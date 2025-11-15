from typing import Any, Dict

import pytest

from backend.app.routers import productos_auth


class FakeScraper:
    def __init__(self, price: float | None):
        self.price = price

    async def get_price(self, url: str) -> float | None:  # pragma: no cover - clarifies signature
        return self.price


def test_crear_producto_registra_historial(monkeypatch, client, auth_headers):
    fake_scraper = FakeScraper(price=120.5)
    monkeypatch.setattr(productos_auth, "scraper", fake_scraper)

    payload: Dict[str, Any] = {
        "nombre": "Laptop Test",
        "url": "https://www.amazon.com/dp/test",
        "precio_objetivo": 200.0
    }

    response = client.post("/api/productos/", json=payload, headers=auth_headers)
    assert response.status_code == 201, response.text

    data = response.json()
    assert data["precio_actual"] == pytest.approx(120.5)
    assert data["num_registros"] == 1
    assert data["tienda"] == "amazon"
    assert data["alerta"] is True

    historial_resp = client.get(f"/api/historial/{data['id']}", headers=auth_headers)
    assert historial_resp.status_code == 200
    historial = historial_resp.json()
    assert len(historial) == 1
    assert historial[0]["precio"] == pytest.approx(120.5)


def test_alertas_endpoint_con_precio_objetivo(monkeypatch, client, auth_headers):
    fake_scraper = FakeScraper(price=90.0)
    monkeypatch.setattr(productos_auth, "scraper", fake_scraper)

    payload = {
        "nombre": "Monitor",
        "url": "https://www.mercadolibre.com.mx/item",
        "precio_objetivo": 95.0
    }

    response = client.post("/api/productos/", json=payload, headers=auth_headers)
    assert response.status_code == 201

    alertas_resp = client.get("/api/alertas/", headers=auth_headers)
    assert alertas_resp.status_code == 200
    alertas = alertas_resp.json()
    assert len(alertas) == 1
    assert alertas[0]["nombre"] == "Monitor"
    assert alertas[0]["precio_actual"] == pytest.approx(90.0)
    assert alertas[0]["ahorro"] == pytest.approx(5.0)