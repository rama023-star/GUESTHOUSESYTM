from conftest import login


def test_login_and_logout(client):
    response = login(client, "admin@example.test", "admin-password")
    assert response.status_code == 200
    assert b"Dashboard" in response.data
    response = client.post("/logout", follow_redirects=True)
    assert b"Sign in" in response.data


def test_bad_password_is_rejected(client):
    response = login(client, "admin@example.test", "incorrect")
    assert b"Email or password is incorrect" in response.data


def test_manager_cannot_access_admin_management(client):
    login(client, "manager@example.test", "manager-password")
    assert client.get("/manage").status_code == 403
