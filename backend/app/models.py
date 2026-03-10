from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum
from datetime import datetime
import enum
from .database import Base


class ChatRequestStatus(str, enum.Enum):
    pending = "pending"
    assigned = "assigned"
    scheduled = "scheduled"


class Role(str, enum.Enum):
    user = "user"
    professional = "professional"
    admin = "admin"


class TriageLabel(str, enum.Enum):
    green = "green"
    yellow = "yellow"
    red = "red"


class UserIdentity(Base):
    __tablename__ = "user_identity"
    id = Column(String(36), primary_key=True)
    clerk_id = Column(String(255), unique=True, nullable=True, index=True)  # Clerk user ID
    email = Column(String(255), unique=True, nullable=True, index=True)
    phone = Column(String(32), unique=True, nullable=True, index=True)
    username = Column(String(64), nullable=True)
    role = Column(SQLEnum(Role), nullable=False, default=Role.user)
    is_anonymous = Column(Boolean, default=False)
    language = Column(String(8), default="en")
    password_hash = Column(String(255), nullable=True)
    is_approved = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    clinical = relationship(
        "UserClinical",
        back_populates="identity",
        uselist=False,
        foreign_keys="UserClinical.user_id",
    )


class UserClinical(Base):
    __tablename__ = "user_clinical"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("user_identity.id"), nullable=False, index=True)
    identity = relationship(
        "UserIdentity",
        back_populates="clinical",
        foreign_keys=[user_id],
    )
    triage_label = Column(SQLEnum(TriageLabel), nullable=True)
    last_assessment_at = Column(DateTime, nullable=True)
    assigned_professional_id = Column(String(36), ForeignKey("user_identity.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Assessment(Base):
    __tablename__ = "assessments"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("user_identity.id"), nullable=False, index=True)
    answers_json = Column(Text, nullable=False)
    triage_label = Column(SQLEnum(TriageLabel), nullable=True)
    risk_score = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("user_identity.id"), nullable=False, index=True)
    bot_type = Column(String(32), default="companion")  # "companion" | "coach"
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(String(36), primary_key=True)
    session_id = Column(String(36), ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(String(16), nullable=False)
    content = Column(Text, nullable=False)
    sentiment_score = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class VoiceSession(Base):
    __tablename__ = "voice_sessions"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("user_identity.id"), nullable=False, index=True)
    professional_id = Column(String(36), ForeignKey("user_identity.id"), nullable=True)
    professional_slug = Column(String(64), nullable=True)  # for mock professionals
    status = Column(String(32), default="requested")
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    actor_id = Column(String(36), nullable=True)
    action = Column(String(64), nullable=False)
    resource = Column(String(64), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ProfessionalChatRequest(Base):
    """Tracks a user's request to chat with a professional through the full lifecycle."""
    __tablename__ = "professional_chat_requests"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("user_identity.id"), nullable=False, index=True)
    message = Column(Text, nullable=True)                           # Optional user message
    status = Column(SQLEnum(ChatRequestStatus), nullable=False, default=ChatRequestStatus.pending)

    # Admin fills these in when assigning
    assigned_professional_name = Column(String(255), nullable=True)
    assigned_professional_id = Column(String(36), nullable=True)   # Optional if professional is in DB

    # Professional fills these in when scheduling
    scheduled_at = Column(DateTime, nullable=True)
    session_notes = Column(Text, nullable=True)                     # Notes from professional for user

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
