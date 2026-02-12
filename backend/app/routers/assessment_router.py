import uuid
import json
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..auth import get_current_user_optional
from ..schemas import AssessmentSubmit, AssessmentResponse
from ..ai.risk import compute_triage_from_answers

router = APIRouter(prefix="/assessment", tags=["assessment"])


@router.post("/submit", response_model=AssessmentResponse)
def submit(body: AssessmentSubmit, db: Session = Depends(get_db), user: models.UserIdentity | None = Depends(get_current_user_optional)):
    user_id = user.id if user else str(uuid.uuid4())
    if not user:
        u = models.UserIdentity(id=user_id, role=models.Role.user, is_anonymous=True, is_approved=True)
        db.add(u)
        db.add(models.UserClinical(id=str(uuid.uuid4()), user_id=user_id))
        db.commit()
    triage_label, risk_score = compute_triage_from_answers(body.answers)
    aid = str(uuid.uuid4())
    db.add(models.Assessment(id=aid, user_id=user_id, answers_json=json.dumps(body.answers), triage_label=triage_label, risk_score=risk_score))
    clinical = db.query(models.UserClinical).filter(models.UserClinical.user_id == user_id).first()
    if clinical:
        clinical.triage_label = triage_label
        clinical.last_assessment_at = datetime.utcnow()
    db.commit()
    redirect = "/user/support" if triage_label == models.TriageLabel.red else "/user"
    return AssessmentResponse(redirect=redirect, triage_label=triage_label)
