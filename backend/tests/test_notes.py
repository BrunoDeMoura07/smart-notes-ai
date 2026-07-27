import pytest


@pytest.fixture()
def logged_in_client(client):
    client.post("/api/auth/register", json={"email": "notes@example.com", "password": "senha12345"})
    client.post("/api/auth/login", json={"email": "notes@example.com", "password": "senha12345"})
    return client


def test_create_text_note_returns_pending(logged_in_client):
    resp = logged_in_client.post("/api/notes", json={"content": "algum conteúdo de teste"})
    assert resp.status_code == 202
    body = resp.json()
    assert body["status"] == "pending"
    assert "id" in body


def test_note_requires_auth(client):
    resp = client.post("/api/notes", json={"content": "sem token"})
    assert resp.status_code in (401, 403)


def test_list_and_get_note(logged_in_client):
    create_resp = logged_in_client.post("/api/notes", json={"content": "nota para listar"})
    note_id = create_resp.json()["id"]

    list_resp = logged_in_client.get("/api/notes")
    assert list_resp.status_code == 200
    assert list_resp.json()["total"] == 1

    get_resp = logged_in_client.get(f"/api/notes/{note_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "pending"


def test_get_note_not_found(logged_in_client):
    resp = logged_in_client.get("/api/notes/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


def test_delete_note(logged_in_client):
    create_resp = logged_in_client.post("/api/notes", json={"content": "nota para apagar"})
    note_id = create_resp.json()["id"]

    delete_resp = logged_in_client.delete(f"/api/notes/{note_id}")
    assert delete_resp.status_code == 204

    get_resp = logged_in_client.get(f"/api/notes/{note_id}")
    assert get_resp.status_code == 404


def test_upload_invalid_file_type(logged_in_client):
    resp = logged_in_client.post(
        "/api/notes/upload",
        files={"file": ("nota.txt", b"conteudo", "text/plain")},
    )
    assert resp.status_code == 400


def test_notes_are_scoped_per_user(logged_in_client):
    create_resp = logged_in_client.post("/api/notes", json={"content": "nota do user 1"})
    note_id = create_resp.json()["id"]

    # Login como o segundo usuário substitui o cookie do usuário 1 neste mesmo client
    # (cookie jar é por instância de TestClient, não por login). Dois usuários autenticados
    # *simultaneamente* exigiriam dois TestClient distintos.
    logged_in_client.post("/api/auth/register", json={"email": "other@example.com", "password": "senha12345"})
    logged_in_client.post("/api/auth/login", json={"email": "other@example.com", "password": "senha12345"})

    resp = logged_in_client.get(f"/api/notes/{note_id}")
    assert resp.status_code == 404
