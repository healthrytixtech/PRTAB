from ..config import settings


def get_reply(message: str, user_id: str | None = None, bot: str = "companion") -> str:
    """Route to the correct chatbot persona based on bot type."""
    if bot == "coach":
        return _coach_reply(message)
    return _companion_reply(message)


# ─── Chatbot 1: AI Companion – Empathetic support ─────────────────────────

def _companion_reply(message: str) -> str:
    msg = message.lower()
    if any(w in msg for w in ["suicide", "kill myself", "end my life", "want to die"]):
        return (
            "I hear how much pain you are in right now, and I am very concerned about you. "
            "Please reach out to iCall immediately at 9152987821 — they are available to help. "
            "You are not alone. Can you tell me a little more about what is happening?"
        )
    if any(w in msg for w in ["help", "sad", "depressed", "crying", "hopeless", "lost"]):
        return (
            "I hear you, and it takes real courage to share what you are feeling. "
            "It is okay to feel this way — your emotions are valid. "
            "Would you like to talk a little more about what has been going on?"
        )
    if any(w in msg for w in ["lonely", "alone", "nobody", "isolated"]):
        return (
            "Loneliness can feel overwhelming. I want you to know that I am here with you right now. "
            "What has contributed to this feeling of being alone — is it something recent?"
        )
    if any(w in msg for w in ["sleep", "insomnia", "can't sleep", "tired"]):
        return (
            "Sleep difficulties often signal that our mind is carrying too much. "
            "Try to keep a consistent bedtime and avoid screens for 30 minutes before bed. "
            "Would you like a short breathing exercise that can help calm your mind tonight?"
        )
    if any(w in msg for w in ["anxious", "anxiety", "panic", "worried", "nervous", "stress"]):
        return (
            "Anxiety can be really overwhelming. Let us try something together — "
            "take a slow breath in for 4 counts, hold for 4, and breathe out for 6. "
            "You are safe here. Can you tell me what is weighing on your mind?"
        )
    if any(w in msg for w in ["angry", "anger", "frustrated", "rage"]):
        return (
            "It is completely natural to feel anger. What matters is how we work through it. "
            "Can you share what triggered these feelings? Sometimes naming it helps."
        )
    if any(w in msg for w in ["thank", "thanks", "helpful", "better", "good"]):
        return (
            "I am so glad I could be here for you 🌿 "
            "Remember, every small step toward wellness counts. "
            "Is there anything else on your mind today?"
        )
    return (
        "Thank you for sharing with me. I am here to listen without judgment. "
        "How are you feeling right now — would you like to explore that a little more?"
    )


# ─── Chatbot 2: MindCoach AI – CBT & Mindfulness ──────────────────────────

def _coach_reply(message: str) -> str:
    msg = message.lower()
    if any(w in msg for w in ["suicide", "kill myself", "end my life", "want to die"]):
        return (
            "What you are experiencing sounds extremely serious, and your safety is the most important thing. "
            "Please contact iCall now at 9152987821. "
            "I am here for you — can you tell me where you are right now?"
        )
    if any(w in msg for w in ["anxious", "anxiety", "panic", "stress", "worried"]):
        return (
            "In CBT, we often start by identifying the thought behind the feeling. "
            "What specific thought or situation triggered this anxiety? "
            "Once we name it, we can examine whether it is an accurate reflection of reality."
        )
    if any(w in msg for w in ["negative", "negative thoughts", "bad thoughts", "cognitive"]):
        return (
            "Cognitive distortions are patterns of thinking that can make us feel worse. "
            "Common ones include catastrophising and all-or-nothing thinking. "
            "Can you share the thought you are stuck on? We can work through it together."
        )
    if any(w in msg for w in ["mindful", "mindfulness", "present", "meditation", "breathe", "breathing"]):
        return (
            "Wonderful that you are exploring mindfulness! Try this: "
            "Notice 5 things you can see, 4 you can physically feel, 3 you can hear, 2 you can smell, 1 you can taste. "
            "This grounds your mind in the present moment. How do you feel after trying that?"
        )
    if any(w in msg for w in ["habit", "routine", "productivity", "motivation", "goal"]):
        return (
            "Building positive habits starts small — what is one 5-minute behaviour you could add to your morning? "
            "In CBT, we call this a behavioural activation. Consistent small actions accumulate into lasting change."
        )
    if any(w in msg for w in ["sleep", "tired", "insomnia"]):
        return (
            "Sleep hygiene is a core part of mental wellness. "
            "CBT for insomnia (CBT-I) recommends using your bed only for sleep, keeping a regular wake time, "
            "and a wind-down routine. Which part of this would you like to work on first?"
        )
    if any(w in msg for w in ["sad", "depressed", "low", "hopeless"]):
        return (
            "Depression often narrows our view of possibilities. "
            "Let us use a technique called behavioural activation — "
            "what is one small, achievable activity that used to bring you joy, even briefly? "
            "Scheduling it can be a first step out of the fog."
        )
    if any(w in msg for w in ["thank", "thanks", "helpful", "better"]):
        return (
            "Great progress! Every session builds your resilience toolkit 🧘 "
            "Remember to practise the techniques between our sessions. "
            "What would you like to focus on next?"
        )
    return (
        "Let us approach this mindfully. "
        "Can you describe what you are experiencing right now — thoughts, feelings, and any physical sensations? "
        "This will help us identify the best CBT or mindfulness technique for your situation."
    )
