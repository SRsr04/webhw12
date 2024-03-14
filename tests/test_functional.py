import pytest
from fastapi.testclient import TestClient
from auth import router

client = TestClient(router)

def test_reset_password():
    response = client.post("/reset-password/", json={"token": "valid_token", "new_password": "new_password"})
    assert response.status_code == 200
    assert response.json() == {"message": "Password reset successful"}