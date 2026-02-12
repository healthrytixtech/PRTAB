from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..auth import require_role

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/queue")
def get_queue(db: Session = Depends(get_db), _user: models.UserIdentity = Depends(require_role(models.Role.admin))):
    clinicals = db.query(models.UserClinical).join(models.UserIdentity, models.UserClinical.user_id == models.UserIdentity.id).filter(models.UserIdentity.role == models.Role.user).limit(50).all()
    return [{"user_id": c.user_id, "triage_label": c.triage_label.value if c.triage_label else None, "assigned_to": c.assigned_professional_id} for c in clinicals]


@router.get("/analytics")
def get_analytics(db: Session = Depends(get_db), _user: models.UserIdentity = Depends(require_role(models.Role.admin))):
    dau = db.query(models.UserIdentity).filter(models.UserIdentity.role == models.Role.user).count()
    return {"dau": dau, "avg_session_minutes": 0, "severity_distribution": {}}
