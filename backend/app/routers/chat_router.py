import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..auth import get_current_user_optional
from ..schemas import ChatMessageIn, ChatMessageOut
from ..ai.chatbot import get_reply

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message", response_model=ChatMessageOut)
def message(
    body: ChatMessageIn,
    bot: str = Query(default="companion", description="Bot type: 'companion' or 'coach'"),
    db: Session = Depends(get_db),
    user: models.UserIdentity | None = Depends(get_current_user_optional),
):
    # Validate bot param
    bot_type = bot if bot in ("companion", "coach") else "companion"

    user_id = user.id if user else None
    reply = get_reply(body.message, user_id=user_id, bot=bot_type)

    if user_id:
        session = (
            db.query(models.ChatSession)
            .filter(
                models.ChatSession.user_id == user_id,
                models.ChatSession.bot_type == bot_type,
            )
            .order_by(models.ChatSession.created_at.desc())
            .first()
        )
        if not session:
            session = models.ChatSession(
                id=str(uuid.uuid4()),
                user_id=user_id,
                bot_type=bot_type,
            )
            db.add(session)
            db.commit()
            db.refresh(session)

        db.add(models.ChatMessage(id=str(uuid.uuid4()), session_id=session.id, role="user", content=body.message))
        db.add(models.ChatMessage(id=str(uuid.uuid4()), session_id=session.id, role="assistant", content=reply))
        db.commit()

    return ChatMessageOut(reply=reply)
