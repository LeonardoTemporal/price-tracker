"""
Tests para el sistema de autenticacion.

Cubre registro de usuarios, login con JWT, y gestion de sesiones.
"""
import pytest
from fastapi.testclient import TestClient


class TestAuthRegistration:
    """Tests para el endpoint de registro de usuarios."""

    def test_registro_usuario_exitoso(self, client: TestClient):
        """Un usuario nuevo debe poder registrarse exitosamente."""
        payload = {
            "email": "nuevo@example.com",
            "username": "nuevousuario",
            "password": "secret123"
        }

        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 201, response.text

        data = response.json()
        assert data["email"] == payload["email"]
        assert data["username"] == payload["username"]
        assert "id" in data
        assert data["is_active"] is True

    def test_registro_email_duplicado(self, client: TestClient):
        """No debe permitir registrar un email ya existente."""
        payload = {
            "email": "duplicado@example.com",
            "username": "usuario1",
            "password": "secret123"
        }

        # Primer registro
        response1 = client.post("/api/auth/register", json=payload)
        assert response1.status_code == 201

        # Segundo registro con mismo email
        payload2 = {
            "email": "duplicado@example.com",
            "username": "usuario2",
            "password": "secret123"
        }
        response2 = client.post("/api/auth/register", json=payload2)
        assert response2.status_code == 400
        assert "email" in response2.json()["detail"].lower()

    def test_registro_username_duplicado(self, client: TestClient):
        """No debe permitir registrar un username ya existente."""
        payload = {
            "email": "user1@example.com",
            "username": "mismouser",
            "password": "secret123"
        }

        client.post("/api/auth/register", json=payload)

        payload2 = {
            "email": "user2@example.com",
            "username": "mismouser",
            "password": "secret123"
        }
        response = client.post("/api/auth/register", json=payload2)
        assert response.status_code == 400
        assert "usuario" in response.json()["detail"].lower()


class TestAuthLogin:
    """Tests para el endpoint de login."""

    def test_login_exitoso(self, client: TestClient):
        """Un usuario registrado debe poder iniciar sesion."""
        # Registrar usuario
        register_payload = {
            "email": "login@test.com",
            "username": "logintest",
            "password": "mypassword"
        }
        client.post("/api/auth/register", json=register_payload)

        # Login
        login_payload = {
            "username": "logintest",
            "password": "mypassword"
        }
        response = client.post("/api/auth/login", data=login_payload)
        assert response.status_code == 200, response.text

        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "logintest"

    def test_login_credenciales_incorrectas(self, client: TestClient):
        """Debe rechazar credenciales incorrectas."""
        login_payload = {
            "username": "nouser",
            "password": "wrongpassword"
        }
        response = client.post("/api/auth/login", data=login_payload)
        assert response.status_code == 401

    def test_login_json_format(self, client: TestClient):
        """El endpoint /login/json debe aceptar JSON."""
        # Registrar
        client.post("/api/auth/register", json={
            "email": "jsonlogin@test.com",
            "username": "jsonlogin",
            "password": "testpass"
        })

        # Login JSON
        response = client.post("/api/auth/login/json", json={
            "username": "jsonlogin",
            "password": "testpass"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()


class TestAuthJWT:
    """Tests para validacion de tokens JWT."""

    def test_acceso_ruta_protegida_con_token(self, client: TestClient, auth_headers: dict):
        """Debe permitir acceso a rutas protegidas con token valido."""
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert "id" in data
        assert "username" in data

    def test_acceso_ruta_protegida_sin_token(self, client: TestClient):
        """Debe rechazar acceso sin token."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_acceso_ruta_protegida_token_invalido(self, client: TestClient):
        """Debe rechazar token invalido."""
        headers = {"Authorization": "Bearer token_invalido"}
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 401


class TestAuthUserManagement:
    """Tests para gestion de usuario (perfil, tema, password)."""

    def test_actualizar_tema(self, client: TestClient, auth_headers: dict):
        """Debe poder actualizar la preferencia de tema oscuro."""
        response = client.put(
            "/api/auth/me/theme",
            json={"dark_mode": True},
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["dark_mode"] is True

    def test_verificar_username_disponible(self, client: TestClient):
        """Debe verificar si un username esta disponible."""
        response = client.get("/api/auth/check-username/nuevousuario12345")
        assert response.status_code == 200
        assert response.json()["available"] is True
