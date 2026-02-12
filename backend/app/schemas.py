from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .models import Role, TriageLabel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: Role


class UserCreate(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    role: Role = Role.user
    is_anonymous: bool = False
    language: Optional[str] = "en"


class UserResponse(BaseModel):
    id: str
    email: Optional[str] = None
    role: Role
    is_anonymous: bool
    is_approved: Optional[bool] = True
    language: Optional[str] = None

    class Config:
        from_attributes = True


class AssessmentSubmit(BaseModel):
    answers: dict[str, str]


class AssessmentResponse(BaseModel):
    redirect: Optional[str] = None
    triage_label: Optional[TriageLabel] = None


class ChatMessageIn(BaseModel):
    message: str


class ChatMessageOut(BaseModel):
    reply: str


class QueueItem(BaseModel):
    user_id: str
    triage_label: Optional[TriageLabel] = None
    last_activity: Optional[datetime] = None
    assigned_to: Optional[str] = None
