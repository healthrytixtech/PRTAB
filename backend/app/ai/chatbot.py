from ..config import settings


def get_reply(message: str, user_id: str | None = None) -> str:
    if settings.ai_provider == "mock":
        return _mock_reply(message)
    # Pluggable: call OpenAI/other adapter here
    return _mock_reply(message)


def _mock_reply(message: str) -> str:
    msg_lower = message.lower()
    if "help" in msg_lower or "sad" in msg_lower:
        return "I hear you. It is okay to feel this way. Would you like to talk more about what is going on?"
    if "sleep" in msg_lower:
        return "Sleep can affect how we feel. Try to keep a regular bedtime and avoid screens before bed. Would you like some breathing exercises?"
    if "anxious" in msg_lower or "anxiety" in msg_lower:
        return "Anxiety can be overwhelming. Take a slow breath. You are safe here. Would you like to try a short grounding exercise?"
    return "Thank you for sharing. I am here to listen. How are you feeling right now?"
