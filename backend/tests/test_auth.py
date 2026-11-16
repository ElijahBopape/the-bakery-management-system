from routers import auth


NEW_USER = {
    "name": "Thandi",
    "email": "thandi@example.com",
    "password": "Secret@123",
    "phone": "0710000000",
}


# ---------- Existing email + password sign in ----------

def test_register_returns_token(client):
    res = client.post("/auth/register", json=NEW_USER)
    assert res.status_code == 201
    body = res.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == NEW_USER["email"]
    assert body["user"]["role"] == "customer"


def test_register_duplicate_email_is_rejected(client):
    client.post("/auth/register", json=NEW_USER)
    res = client.post("/auth/register", json=NEW_USER)
    assert res.status_code == 400


def test_login_with_correct_password(client):
    client.post("/auth/register", json=NEW_USER)
    res = client.post(
        "/auth/login",
        json={"email": NEW_USER["email"], "password": NEW_USER["password"]},
    )
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_with_wrong_password_fails(client):
    client.post("/auth/register", json=NEW_USER)
    res = client.post(
        "/auth/login", json={"email": NEW_USER["email"], "password": "wrong"}
    )
    assert res.status_code == 401


def test_me_requires_token(client):
    res = client.get("/auth/me")
    assert res.status_code in (401, 403)


def test_me_returns_profile_with_token(client):
    token = client.post("/auth/register", json=NEW_USER).json()["access_token"]
    res = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == NEW_USER["email"]


# ---------- Google sign in ----------
# We never call the real Google here: verify_oauth2_token is replaced by a fake.

def fake_google(monkeypatch, info=None, error=False):
    monkeypatch.setattr(auth, "GOOGLE_CLIENT_ID", "test-client-id")

    def fake_verify(token, request, audience):
        if error:
            raise ValueError("bad token")
        assert audience == "test-client-id"
        return info

    monkeypatch.setattr(auth.id_token, "verify_oauth2_token", fake_verify)


def test_google_login_creates_new_customer(client, monkeypatch):
    fake_google(monkeypatch, {"email": "Lerato@Gmail.com", "email_verified": True, "name": "Lerato M"})
    res = client.post("/auth/google", json={"credential": "fake-token"})
    assert res.status_code == 200
    body = res.json()
    assert body["user"]["email"] == "lerato@gmail.com"
    assert body["user"]["name"] == "Lerato M"
    assert body["user"]["role"] == "customer"
    assert body["access_token"]


def test_google_login_reuses_existing_account(client, monkeypatch):
    client.post("/auth/register", json=NEW_USER)
    fake_google(monkeypatch, {"email": NEW_USER["email"], "email_verified": True, "name": "Thandi"})
    first = client.post("/auth/google", json={"credential": "fake-token"}).json()
    second = client.post("/auth/google", json={"credential": "fake-token"}).json()
    assert first["user"]["id"] == second["user"]["id"] == 1


def test_google_token_works_on_protected_routes(client, monkeypatch):
    fake_google(monkeypatch, {"email": "a@b.com", "email_verified": True, "name": "A"})
    token = client.post("/auth/google", json={"credential": "x"}).json()["access_token"]
    res = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "a@b.com"


def test_google_invalid_token_is_rejected(client, monkeypatch):
    fake_google(monkeypatch, error=True)
    res = client.post("/auth/google", json={"credential": "garbage"})
    assert res.status_code == 401


def test_google_unverified_email_is_rejected(client, monkeypatch):
    fake_google(monkeypatch, {"email": "x@y.com", "email_verified": False, "name": "X"})
    res = client.post("/auth/google", json={"credential": "fake-token"})
    assert res.status_code == 401


def test_google_not_configured_returns_500(client, monkeypatch):
    monkeypatch.setattr(auth, "GOOGLE_CLIENT_ID", "")
    res = client.post("/auth/google", json={"credential": "fake-token"})
    assert res.status_code == 500