from uptime.config import settings

def test_healthz(client):
    assert client.get("/healthz").json() == {"status": "ok"}

def test_readyz(client):
    assert client.get("/readyz").status_code == 200

def test_create_and_list_monitor(client):
    created = client.post("/api/monitors", json={"name": "Example", "url": "https://example.com"})
    assert created.status_code == 201

    monitors = client.get("/api/monitors").json()
    assert len(monitors) == 1
    assert monitors[0]["name"] == "Example"
    assert monitors[0]["is_up"] is None 


def test_rejects_invalid_url(client):
    response = client.post("/api/monitors", json={"name": "Bad", "url": "not-a-url"})
    assert response.status_code == 422

def test_delete_monitor(client):
    monitor_id = client.post(
        "/api/monitors", json={"name": "Example", "url": "https://example.com"}
    ).json()["id"]

    assert client.delete(f"/api/monitors/{monitor_id}").status_code == 204
    assert client.get("/api/monitors").json() == []
    assert client.delete(f"/api/monitors/{monitor_id}").status_code == 404


def test_admin_token_required_when_configured(client, monkeypatch):
    monkeypatch.setattr(settings, "admin_token", "s3cret")
    payload = {"name": "Example", "url": "https://example.com"}

    assert client.post("/api/monitors", json=payload).status_code == 401
    authorized = client.post(
        "/api/monitors", json=payload, headers={"Authorization": "Bearer s3cret"}
    )
    assert authorized.status_code == 201


def test_status_page_renders(client):
    client.post("/api/monitors", json={"name": "Example", "url": "https://example.com"})
    response = client.get("/")
    assert response.status_code == 200
    assert "Example" in response.text