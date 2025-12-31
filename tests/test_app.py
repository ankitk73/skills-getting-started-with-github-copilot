import pytest
from httpx import AsyncClient, ASGITransport
from src.app import app

@pytest.mark.asyncio
async def test_get_activities():
    async with AsyncClient(transport=ASGITransport(app), base_url="http://testserver") as client:
        response = await client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Basketball Team" in data
        assert "participants" in data["Basketball Team"]

@pytest.mark.asyncio
async def test_signup_for_activity():
    async with AsyncClient(transport=ASGITransport(app), base_url="http://testserver") as client:
        # First, get initial participants
        response = await client.get("/activities")
        initial_data = response.json()
        initial_count = len(initial_data["Basketball Team"]["participants"])

        # Signup
        response = await client.post("/activities/Basketball%20Team/signup?email=test@example.com")
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

        # Check updated
        response = await client.get("/activities")
        updated_data = response.json()
        assert len(updated_data["Basketball Team"]["participants"]) == initial_count + 1
        assert "test@example.com" in updated_data["Basketball Team"]["participants"]

@pytest.mark.asyncio
async def test_signup_duplicate():
    async with AsyncClient(transport=ASGITransport(app), base_url="http://testserver") as client:
        # Signup first time
        response = await client.post("/activities/Basketball%20Team/signup?email=duplicate@example.com")
        assert response.status_code == 200

        # Signup again
        response = await client.post("/activities/Basketball%20Team/signup?email=duplicate@example.com")
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

@pytest.mark.asyncio
async def test_unregister():
    async with AsyncClient(transport=ASGITransport(app), base_url="http://testserver") as client:
        # Signup first
        await client.post("/activities/Soccer%20Club/signup?email=unregister@example.com")

        # Unregister
        response = await client.delete("/activities/Soccer%20Club/unregister?email=unregister@example.com")
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

        # Check removed
        response = await client.get("/activities")
        data = response.json()
        assert "unregister@example.com" not in data["Soccer Club"]["participants"]

@pytest.mark.asyncio
async def test_unregister_not_signed_up():
    async with AsyncClient(transport=ASGITransport(app), base_url="http://testserver") as client:
        response = await client.delete("/activities/Art%20Club/unregister?email=notsigned@example.com")
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

@pytest.mark.asyncio
async def test_activity_not_found():
    async with AsyncClient(transport=ASGITransport(app), base_url="http://testserver") as client:
        response = await client.post("/activities/Nonexistent/signup?email=test@example.com")
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_root_redirect():
    async with AsyncClient(transport=ASGITransport(app), base_url="http://testserver") as client:
        response = await client.get("/")
        assert response.status_code == 307  # RedirectResponse returns 307