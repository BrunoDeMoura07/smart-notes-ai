def test_register_and_login(client):
    resp = client.post(
        "/api/auth/register", json={"email": "user@example.com", "password": "senha12345"}
    )
    assert resp.status_code == 201
    assert resp.json()["email"] == "user@example.com"

    resp = client.post(
        "/api/auth/login", json={"email": "user@example.com", "password": "senha12345"}
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    assert token

    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "user@example.com"


def test_register_duplicate_email(client):
    client.post("/api/auth/register", json={"email": "dup@example.com", "password": "senha12345"})
    resp = client.post(
        "/api/auth/register", json={"email": "dup@example.com", "password": "outrasenha"}
    )
    assert resp.status_code == 409


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={"email": "wrong@example.com", "password": "senha12345"})
    resp = client.post(
        "/api/auth/login", json={"email": "wrong@example.com", "password": "errada"}
    )
    assert resp.status_code == 401


def test_me_without_token(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code in (401, 403)
