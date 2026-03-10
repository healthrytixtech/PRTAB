from fastapi.testclient import TestClient

from app import models


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_signup_and_me_flow(client: TestClient):
    # User signs up with email/password
    resp = client.post(
        "/auth/signup",
        json={
            "email": "user@example.com",
            "password": "StrongPass123!",
            "role": "user",
            "is_anonymous": False,
            "language": "en",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    token = data["access_token"]

    # /auth/me should reflect the created user
    me = client.get("/auth/me", headers=auth_header(token))
    assert me.status_code == 200
    me_data = me.json()
    assert me_data["email"] == "user@example.com"
    assert me_data["role"] == models.Role.user.value
    assert me_data["is_anonymous"] is False


def test_anonymous_login_creates_user_and_clinical_record(client: TestClient, db_session):
    # Anonymous login (no email/password) should succeed
    resp = client.post("/auth/login", json={})
    assert resp.status_code == 200
    data = resp.json()
    token = data["access_token"]

    # /auth/me should show an anonymous, approved user
    me = client.get("/auth/me", headers=auth_header(token))
    assert me.status_code == 200
    me_data = me.json()
    assert me_data["is_anonymous"] is True
    assert me_data["role"] == models.Role.user.value

    # There should be a linked UserClinical record
    user = db_session.query(models.UserIdentity).filter_by(id=me_data["id"]).first()
    assert user is not None
    clinical = db_session.query(models.UserClinical).filter_by(user_id=user.id).first()
    assert clinical is not None


def test_professional_requires_approval_before_login(client: TestClient, db_session):
    # Sign up as professional (starts as not approved)
    resp = client.post(
        "/auth/signup",
        json={
            "email": "pro@example.com",
            "password": "StrongPass123!",
            "role": "professional",
        },
    )
    assert resp.status_code == 200
    user_id = resp.json()["user_id"]

    # Attempt to log in should be forbidden until approved
    login = client.post(
        "/auth/login",
        json={"email": "pro@example.com", "password": "StrongPass123!"},
    )
    assert login.status_code == 403

    # Approve the professional directly in the database
    pro = db_session.query(models.UserIdentity).filter_by(id=user_id).first()
    assert pro is not None
    pro.is_approved = True
    db_session.commit()

    # Login should now succeed
    login2 = client.post(
        "/auth/login",
        json={"email": "pro@example.com", "password": "StrongPass123!"},
    )
    assert login2.status_code == 200
    data = login2.json()
    assert data["role"] == models.Role.professional.value

