import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from .. import models
from ..auth import get_current_user, get_current_user_optional, require_role

router = APIRouter(tags=["professionals"])


# ─── Pydantic schemas ─────────────────────────────────────────────────────

class ChatRequestCreate(BaseModel):
    message: Optional[str] = None  # Optional message from user about their concern


class AssignRequest(BaseModel):
    professional_name: str  # Admin types in the professional's name to assign


class ScheduleRequest(BaseModel):
    scheduled_at: str          # ISO datetime string e.g. "2025-03-01T10:30:00"
    session_notes: Optional[str] = None


# ─── Endpoints ────────────────────────────────────────────────────────────

@router.post("/chat-requests", status_code=status.HTTP_201_CREATED)
def create_chat_request(
    body: ChatRequestCreate,
    db: Session = Depends(get_db),
    user: models.UserIdentity = Depends(get_current_user),
):
    """User creates a request to chat with a professional."""
    # Check if user already has a pending/assigned request
    existing = db.query(models.ProfessionalChatRequest).filter(
        models.ProfessionalChatRequest.user_id == user.id,
        models.ProfessionalChatRequest.status.in_([
            models.ChatRequestStatus.pending,
            models.ChatRequestStatus.assigned,
        ])
    ).first()
    if existing:
        return {"id": existing.id, "status": existing.status, "already_exists": True}

    req = models.ProfessionalChatRequest(
        id=str(uuid.uuid4()),
        user_id=user.id,
        message=body.message,
        status=models.ChatRequestStatus.pending,
    )
    db.add(req)
    db.add(models.AuditLog(
        actor_id=user.id,
        action="chat_request_created",
        resource="professional_chat_request",
        details=body.message or "No message",
    ))
    db.commit()
    db.refresh(req)
    return {"id": req.id, "status": req.status, "created_at": req.created_at.isoformat()}


@router.get("/chat-requests/mine")
def get_my_chat_request(
    db: Session = Depends(get_db),
    user: models.UserIdentity = Depends(get_current_user),
):
    """User checks their latest chat request status."""
    req = db.query(models.ProfessionalChatRequest).filter(
        models.ProfessionalChatRequest.user_id == user.id
    ).order_by(models.ProfessionalChatRequest.created_at.desc()).first()

    if not req:
        return {"status": "none"}

    return {
        "id": req.id,
        "status": req.status,
        "message": req.message,
        "assigned_professional_name": req.assigned_professional_name,
        "scheduled_at": req.scheduled_at.isoformat() if req.scheduled_at else None,
        "session_notes": req.session_notes,
        "created_at": req.created_at.isoformat(),
    }


@router.get("/chat-requests")
def list_chat_requests(
    db: Session = Depends(get_db),
    _admin: models.UserIdentity = Depends(require_role(models.Role.admin)),
):
    """Admin: list all chat requests ordered by creation time (newest first)."""
    requests = db.query(models.ProfessionalChatRequest).order_by(
        models.ProfessionalChatRequest.created_at.desc()
    ).all()

    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "message": r.message,
            "status": r.status,
            "assigned_professional_name": r.assigned_professional_name,
            "scheduled_at": r.scheduled_at.isoformat() if r.scheduled_at else None,
            "created_at": r.created_at.isoformat(),
        }
        for r in requests
    ]


@router.put("/chat-requests/{request_id}/assign")
def assign_professional(
    request_id: str,
    body: AssignRequest,
    db: Session = Depends(get_db),
    admin: models.UserIdentity = Depends(require_role(models.Role.admin)),
):
    """Admin assigns a professional by name to a pending request."""
    req = db.query(models.ProfessionalChatRequest).filter(
        models.ProfessionalChatRequest.id == request_id
    ).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    req.assigned_professional_name = body.professional_name
    req.status = models.ChatRequestStatus.assigned
    req.updated_at = datetime.utcnow()
    db.add(
        models.AuditLog(
            actor_id=admin.id,
            action="chat_request_assigned",
            resource="professional_chat_request",
            details=f"Request {request_id} assigned to {body.professional_name}",
        )
    )
    db.commit()
    db.refresh(req)
    return {"id": req.id, "status": req.status, "assigned_professional_name": req.assigned_professional_name}


@router.put("/chat-requests/{request_id}/schedule")
def set_schedule(
    request_id: str,
    body: ScheduleRequest,
    db: Session = Depends(get_db),
    professional: models.UserIdentity = Depends(require_role(models.Role.professional)),
):
    """Professional sets a schedule for an assigned request."""
    req = db.query(models.ProfessionalChatRequest).filter(
        models.ProfessionalChatRequest.id == request_id
    ).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    req.scheduled_at = datetime.fromisoformat(body.scheduled_at)
    req.session_notes = body.session_notes
    req.status = models.ChatRequestStatus.scheduled
    req.updated_at = datetime.utcnow()
    db.add(
        models.AuditLog(
            actor_id=professional.id,
            action="chat_request_scheduled",
            resource="professional_chat_request",
            details=f"Request {request_id} scheduled for {body.scheduled_at}",
        )
    )
    db.commit()
    db.refresh(req)
    return {
        "id": req.id,
        "status": req.status,
        "scheduled_at": req.scheduled_at.isoformat(),
        "session_notes": req.session_notes,
    }
