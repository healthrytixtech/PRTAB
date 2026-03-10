from fastapi.testclient import TestClient

from app import models


def test_assessment_anonymous_creates_user_and_triage_label_set(client: TestClient, db_session):
    answers = {
        "q1": "I feel down and tired",
        "q2": "I have trouble sleeping",
    }
    resp = client.post("/assessment/submit", json={"answers": answers})
    assert resp.status_code == 200
    data = resp.json()

    # Triage label should be a valid enum value and redirect should be consistent
    assert data["triage_label"] in {
        models.TriageLabel.green.value,
        models.TriageLabel.yellow.value,
        models.TriageLabel.red.value,
    }
    assert data["redirect"] in {"/user", "/user/support"}

    # The created user should have a clinical record with a matching triage label
    assessment = db_session.query(models.Assessment).first()
    assert assessment is not None
    user_clinical = (
        db_session.query(models.UserClinical)
        .filter_by(user_id=assessment.user_id)
        .first()
    )
    assert user_clinical is not None
    assert user_clinical.triage_label == assessment.triage_label

