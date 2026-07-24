import pytest


@pytest.fixture()
def auth_headers(client):
    client.post("/api/auth/register", json={"email": "notes@example.com", "password": "senha12345"})
    resp = client.post("/api/auth/login", json={"email": "notes@example.com", "password": "senha12345"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_text_note_returns_pending(client, auth_headers):
    resp = client.post("/api/notes", json={"content": "algum conteúdo de teste"}, headers=auth_headers)
    assert resp.status_code == 202
    body = resp.json()
    assert body["status"] == "pending"
    assert "id" in body


def test_note_requires_auth(client):
    resp = client.post("/api/notes", json={"content": "sem token"})
    assert resp.status_code in (401, 403)


def test_list_and_get_note(client, auth_headers):
    create_resp = client.post(
        "/api/notes", json={"content": "nota para listar"}, headers=auth_headers
    )
    note_id = create_resp.json()["id"]

    list_resp = client.get("/api/notes", headers=auth_headers)
    assert list_resp.status_code == 200
    assert list_resp.json()["total"] == 1

    get_resp = client.get(f"/api/notes/{note_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "pending"


def test_get_note_not_found(client, auth_headers):
    resp = client.get(
        "/api/notes/00000000-0000-0000-0000-000000000000", headers=auth_headers
    )
    assert resp.status_code == 404


def test_delete_note(client, auth_headers):
    create_resp = client.post(
        "/api/notes", json={"content": "nota para apagar"}, headers=auth_headers
    )
    note_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/api/notes/{note_id}", headers=auth_headers)
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/api/notes/{note_id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_upload_invalid_file_type(client, auth_headers):
    resp = client.post(
        "/api/notes/upload",
        files={"file": ("nota.txt", b"conteudo", "text/plain")},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_notes_are_scoped_per_user(client, auth_headers):
    create_resp = client.post(
        "/api/notes", json={"content": "nota do user 1"}, headers=auth_headers
    )
    note_id = create_resp.json()["id"]

    client.post("/api/auth/register", json={"email": "other@example.com", "password": "senha12345"})
    other_login = client.post(
        "/api/auth/login", json={"email": "other@example.com", "password": "senha12345"}
    )
    other_headers = {"Authorization": f"Bearer {other_login.json()['access_token']}"}

    resp = client.get(f"/api/notes/{note_id}", headers=other_headers)
    assert resp.status_code == 404
