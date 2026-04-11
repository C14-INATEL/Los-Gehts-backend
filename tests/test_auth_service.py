import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from main import app


# ── MOCKS (HTTP layer) ────────────────────────────────────────────────────────

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


# ── FIXTURES (HTTP layer) ─────────────────────────────────────────────────────

@pytest.fixture
def client():
    from features.auth import router
    router.auth_service = MockAuthService()
    return TestClient(app)


@pytest.fixture
def client_error():
    from features.auth import router
    router.auth_service = MockAuthServiceError()
    return TestClient(app)


# ── HELPERS (unit layer) ──────────────────────────────────────────────────────

def make_service(existing_user=None, created_user=None):
    """Build an AuthService with fully mocked dependencies."""
    db = MagicMock()
    db.user.find_unique = AsyncMock(return_value=existing_user)
    db.user.create = AsyncMock(return_value=created_user)

    jwt = MagicMock()
    jwt.create_token = MagicMock(return_value="fake-jwt-token")

    from features.auth.service import AuthService
    return AuthService(db=db, jwtHandler=jwt), db, jwt


def make_user(id=1, username="alice", password="secret"):
    user = MagicMock()
    user.id = id
    user.username = username
    user.password = password
    return user


# ── TESTES HTTP (1–4) ─────────────────────────────────────────────────────────

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


# ── TESTES UNITÁRIOS — register (5–8) ────────────────────────────────────────

# teste 5: register chama find_unique com o username correto
@pytest.mark.asyncio
async def test_register_queries_correct_username():
    service, db, _ = make_service(existing_user=None, created_user=make_user())
    await service.register("alice", "SenhaSegura123!!!")
    db.user.find_unique.assert_called_once_with(where={"username": "alice"})


# teste 6: register lança ValueError se o username já existe
@pytest.mark.asyncio
async def test_register_raises_if_username_taken():
    service, _, _ = make_service(existing_user=make_user())
    with pytest.raises(ValueError, match="Username already registered"):
        await service.register("alice", "SenhaSegura123!!!")


# teste 7: register cria o usuário com os dados corretos
@pytest.mark.asyncio
async def test_register_creates_user_with_correct_data():
    new_user = make_user()
    service, db, _ = make_service(existing_user=None, created_user=new_user)
    await service.register("alice", "SenhaSegura123!!!")
    db.user.create.assert_called_once_with(data={"username": "alice", "password": "SenhaSegura123!!!"})


# teste 8: register retorna o token gerado pelo jwtHandler
@pytest.mark.asyncio
async def test_register_returns_token():
    service, _, jwt = make_service(existing_user=None, created_user=make_user(id=42))
    token = await service.register("alice", "SenhaSegura123!!!")
    jwt.create_token.assert_called_once_with(42)
    assert token == "fake-jwt-token"


# ── TESTES UNITÁRIOS — login (9–12) ──────────────────────────────────────────

# teste 9: login lança ValueError se o usuário não existe
@pytest.mark.asyncio
async def test_login_raises_if_user_not_found():
    service, _, _ = make_service(existing_user=None)
    with pytest.raises(ValueError, match="Invalid credentials"):
        await service.login("ghost", "SenhaSegura123!!!")


# teste 10: login lança ValueError se a senha está errada
@pytest.mark.asyncio
async def test_login_raises_if_wrong_password():
    service, _, _ = make_service(existing_user=make_user(password="correct"))
    with pytest.raises(ValueError, match="Invalid credentials"):
        await service.login("alice", "wrong")


# teste 11: login chama find_unique com o username correto
@pytest.mark.asyncio
async def test_login_queries_correct_username():
    service, db, _ = make_service(existing_user=make_user(password="SenhaSegura123!!!"))
    await service.login("alice", "SenhaSegura123!!!")
    db.user.find_unique.assert_called_once_with(where={"username": "alice"})


# teste 12: login retorna o token gerado pelo jwtHandler
@pytest.mark.asyncio
async def test_login_returns_token():
    service, _, jwt = make_service(existing_user=make_user(id=7, password="SenhaSegura123!!!"))
    token = await service.login("alice", "SenhaSegura123!!!")
    jwt.create_token.assert_called_once_with(7)
    assert token == "fake-jwt-token"
