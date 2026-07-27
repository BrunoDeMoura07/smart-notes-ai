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
    assert resp.json()["email"] == "user@example.com"
    assert "access_token" not in resp.json()

    resp = client.get("/api/auth/me")
    assert resp.status_code == 200
    assert resp.json()["email"] == "user@example.com"


def test_login_sets_httponly_cookie(client):
    client.post("/api/auth/register", json={"email": "cookie@example.com", "password": "senha12345"})
    resp = client.post(
        "/api/auth/login", json={"email": "cookie@example.com", "password": "senha12345"}
    )
    assert "access_token" in resp.cookies
    set_cookie_header = resp.headers.get("set-cookie", "")
    assert "HttpOnly" in set_cookie_header
    assert "samesite=lax" in set_cookie_header.lower()


def test_logout_clears_cookie(client):
    client.post("/api/auth/register", json={"email": "logout@example.com", "password": "senha12345"})
    client.post("/api/auth/login", json={"email": "logout@example.com", "password": "senha12345"})

    resp = client.post("/api/auth/logout")
    assert resp.status_code == 204

    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


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


def test_me_without_cookie(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code in (401, 403)
