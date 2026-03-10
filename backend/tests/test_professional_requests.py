from fastapi.testclient import TestClient

from app import models
from app.auth import create_access_token


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _signup_user(client: TestClient, email: str, role: str = "user") -> tuple[str, str]:
    resp = client.post(
        "/auth/signup",
        json={"email": email, "password": "StrongPass123!", "role": role},
    )
    assert resp.status_code == 200
    data = resp.json()
    return data["user_id"], data["access_token"]


def test_user_creates_and_reads_own_chat_request(client: TestClient, db_session):
    user_id, token = _signup_user(client, "requser@example.com")

    # Create chat request
    resp = client.post(
        "/chat-requests",
        json={"message": "I would like to talk to a professional."},
        headers=_auth_header(token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == models.ChatRequestStatus.pending.value

    # User should see their latest request via /chat-requests/mine
    mine = client.get("/chat-requests/mine", headers=_auth_header(token))
    assert mine.status_code == 200
    mine_data = mine.json()
    assert mine_data["id"] == data["id"]
    assert mine_data["message"] == "I would like to talk to a professional."


def test_admin_can_manage_chat_requests_and_audit_logs(client: TestClient, db_session):
    # Create a normal user and chat request
    user_id, user_token = _signup_user(client, "queueuser@example.com")
    resp = client.post(
        "/chat-requests",
        json={"message": "Need help with anxiety."},
        headers=_auth_header(user_token),
    )
    assert resp.status_code == 201
    request_id = resp.json()["id"]

    # Promote a second user to admin directly in the DB
    admin_user = models.UserIdentity(
        id="admin-1",
        email="admin@example.com",
        role=models.Role.admin,
        is_anonymous=False,
        is_approved=True,
    )
    db_session.add(admin_user)
    db_session.commit()

    admin_token = create_access_token(data={"sub": admin_user.id, "role": admin_user.role.value})

    # Admin can list all chat requests
    listing = client.get("/chat-requests", headers=_auth_header(admin_token))
    assert listing.status_code == 200
    items = listing.json()
    assert any(item["id"] == request_id for item in items)

    # Admin assigns a professional
    assign = client.put(
        f"/chat-requests/{request_id}/assign",
        json={"professional_name": "Dr. Smith"},
        headers=_auth_header(admin_token),
    )
    assert assign.status_code == 200
    assign_data = assign.json()
    assert assign_data["assigned_professional_name"] == "Dr. Smith"
    assert assign_data["status"] == models.ChatRequestStatus.assigned.value

    # Admin (acting as professional) schedules the session
    schedule = client.put(
        f"/chat-requests/{request_id}/schedule",
        json={"scheduled_at": "2030-01-01T10:00:00", "session_notes": "Initial intake"},
        headers=_auth_header(admin_token),
    )
    assert schedule.status_code == 200
    schedule_data = schedule.json()
    assert schedule_data["status"] == models.ChatRequestStatus.scheduled.value

    # Audit logs should record assignment and scheduling with actor_id
    logs = db_session.query(models.AuditLog).all()
    actions = {log.action for log in logs}
    assert "chat_request_assigned" in actions
    assert "chat_request_scheduled" in actions
    # Ensure at least one log entry for each action is attributed to the admin user
    assert any(log.actor_id == admin_user.id and log.action == "chat_request_assigned" for log in logs)
    assert any(log.actor_id == admin_user.id and log.action == "chat_request_scheduled" for log in logs)


def test_unauthorized_cannot_access_admin_chat_request_endpoints(client: TestClient):
    # Regular user token
    _, token = _signup_user(client, "nonadmin@example.com")

    # Listing all requests should be forbidden
    resp = client.get("/chat-requests", headers=_auth_header(token))
    assert resp.status_code == 403

