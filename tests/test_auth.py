from unittest.mock import patch
from fastapi.testclient import TestClient
from auth import router

client = TestClient(router)

@patch("auth.get_user_by_email")
@patch("auth.update_user_password")
def test_reset_password_success(update_user_password_mock, get_user_by_email_mock):
    # Mock the get_user_by_email function to return a user
    get_user_by_email_mock.return_value = {"id": 1}
    # Mock the update_user_password function
    update_user_password_mock.return_value = None

    token = "valid_reset_token"
    new_password = "new_password"
    response = client.post("/reset-password/", json={"token": token, "new_password": new_password})

    assert response.status_code == 200
    assert response.json() == {"message": "Password reset successful"}

@patch("auth.get_user_by_email")
def test_reset_password_user_not_found(get_user_by_email_mock):
    # Mock the get_user_by_email function to return None (user not found)
    get_user_by_email_mock.return_value = None

    token = "valid_reset_token"
    new_password = "new_password"
    response = client.post("/reset-password/", json={"token": token, "new_password": new_password})

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}