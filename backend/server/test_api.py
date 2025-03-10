import pytest
from httpx import AsyncClient
from main import app

API_URL = "http://127.0.0.1:8000"

@pytest.mark.asyncio
async def test_register():
    async with AsyncClient(base_url=API_URL) as client:
        response = await client.post("/register/", json={"email": "qwerty@example.com", "password": "123456000"})
        assert response.status_code == 200
        assert "message" in response.json()

@pytest.mark.asyncio
async def test_login():
    async with AsyncClient(base_url=API_URL) as client:
        response = await client.post("/token", data={"username": "test@example.com", "password": "123456"})
        assert response.status_code == 200
        assert "access_token" in response.json()
        return response.json()["access_token"]

@pytest.mark.asyncio
async def test_create_task():
    token = await test_login()
    async with AsyncClient(base_url=API_URL, headers={"Authorization": f"Bearer {token}"}) as client:
        response = await client.post("/tasks/", json={"title": "Тестовая задача", "description": "Описание", "status": "новая", "deadline": "2025-12-31T23:59:59"})
        assert response.status_code == 200
        assert "message" in response.json()
        return response.json()["id"]

@pytest.mark.asyncio
async def test_get_tasks():
    token = await test_login()
    async with AsyncClient(base_url=API_URL, headers={"Authorization": f"Bearer {token}"}) as client:
        response = await client.get("/tasks/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_update_task():
    token = await test_login()
    task_id = await test_create_task()
    async with AsyncClient(base_url=API_URL, headers={"Authorization": f"Bearer {token}"}) as client:
        response = await client.patch(f"/tasks/{task_id}", json={"status": "completed"})
        assert response.status_code == 200
        assert response.json()["message"] == "Статус задачи обновлен"

@pytest.mark.asyncio
async def test_delete_task():
    token = await test_login()
    task_id = await test_create_task()
    async with AsyncClient(base_url=API_URL, headers={"Authorization": f"Bearer {token}"}) as client:
        response = await client.delete(f"/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Задача успешно удалена"
