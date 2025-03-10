import pytest
from httpx import AsyncClient
from main import app

API_URL = "http://127.0.0.1:8000"


@pytest.fixture
async def client():
    """Фикстура для создания асинхронного клиента."""
    async with AsyncClient(app=app, base_url=API_URL) as ac:
        yield ac


@pytest.fixture
async def auth_token(client):
    """Фикстура для получения токена после регистрации и входа."""
    await client.post("/register/", json={"email": "test@example.com", "password": "123456"})

    response = await client.post("/token", data={"username": "test@example.com", "password": "123456"})
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
async def created_task(client, auth_token):
    """Фикстура для создания тестовой задачи."""
    response = await client.post(
        "/tasks/",
        json={
            "title": "Тестовая задача",
            "description": "Описание задачи",
            "status": "новая",
            "deadline": "2025-12-31T23:59:59",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    return response.json()["id"]


@pytest.mark.asyncio
async def test_register(client):
    """Тест регистрации пользователя."""
    response = await client.post("/register/", json={"email": "qwerty@example.com", "password": "123456000"})
    assert response.status_code in [200, 400]  # 400 если пользователь уже зарегистрирован
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_login(client):
    """Тест входа и получения токена."""
    response = await client.post("/token", data={"username": "test@example.com", "password": "123456"})
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_create_task(client, auth_token):
    """Тест создания задачи."""
    response = await client.post(
        "/tasks/",
        json={
            "title": "Тестовая задача",
            "description": "Описание",
            "status": "новая",
            "deadline": "2025-12-31T23:59:59",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_get_tasks(client, auth_token):
    """Тест получения списка задач."""
    response = await client.get("/tasks/", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_update_task(client, auth_token, created_task):
    """Тест обновления статуса задачи."""
    response = await client.patch(
        f"/tasks/{created_task}",
        json={"status": "completed"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Статус задачи обновлен"


@pytest.mark.asyncio
async def test_delete_task(client, auth_token, created_task):
    """Тест удаления задачи."""
    response = await client.delete(
        f"/tasks/{created_task}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Задача успешно удалена"
