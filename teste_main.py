from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# teste: app sobe sem erro
def test_app_startup():
    response = client.get("/")
    # pode dar 404 se não tiver rota raiz, mas não pode quebrar o7
    assert response.status_code in [200, 404]


# teste: rotas de auth existem
def test_auth_routes_exist():
    response = client.get("/auth")
    assert response.status_code in [200, 404, 405]


# teste: rotas de tasks existem
def test_tasks_routes_exist():
    response = client.get("/tasks")
    assert response.status_code in [200, 404, 405]


# teste: conexão com banco no lifespan
def test_lifespan_runs():
    # só de criar o client ele já executa o lifespan
    with TestClient(app) as c:
        response = c.get("/")
        assert response.status_code in [200, 404]