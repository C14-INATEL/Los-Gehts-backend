import pytest
from fastapi.testclient import TestClient
from main import app  # importa sua aplicação principal


# MOCKS (pra simular o comportamento do AuthService):

class MockAuthService:
    async def register(self, username, password):
        return "fake-jwt-token"

    async def login(self, username, password):
        return "fake-jwt-token"


class MockAuthServiceError:
    async def register(self, username, password):
        raise ValueError("Erro ao registrar")

    async def login(self, username, password):
        raise ValueError("Credenciais inválidas")


# FIXTURES (configurar o ambiente de teste):

@pytest.fixture
def client():
    from features.auth import router

    # usa o mock de SUCESSO
    router.auth_service = MockAuthService()

    return TestClient(app)


@pytest.fixture
def client_error():
    from features.auth import router

    # usa o mock de ERRO
    router.auth_service = MockAuthServiceError()

    return TestClient(app)


# TESTES UNITÁRIOS:

# teste 1: register com sucesso
def test_register_success(client):
    response = client.post(
        "/auth/register",
        json={"username": "teste", "password": "123"}
    )

    assert response.status_code == 201
    assert response.json() == {"JWT": "fake-jwt-token"}


# teste 2: register com erro
def test_register_error(client_error):
    response = client_error.post(
        "/auth/register",
        json={"username": "teste", "password": "123"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Erro ao registrar"


# teste 3: login com sucesso
def test_login_success(client):
    response = client.post(
        "/auth/login",
        json={"username": "teste", "password": "123"}
    )

    assert response.status_code == 200
    assert response.json() == {"JWT": "fake-jwt-token"}


# teste 4: login com erro
def test_login_error(client_error):
    response = client_error.post(
        "/auth/login",
        json={"username": "teste", "password": "123"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciais inválidas"