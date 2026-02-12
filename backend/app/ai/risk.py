from .. import models


def compute_triage_from_answers(answers: dict) -> tuple:
    risk = 0
    for k, v in answers.items():
        if isinstance(v, str):
            v_lower = v.lower()
            if "very low" in v_lower or "anxious" in v_lower or "no" in v_lower or "tired" in v_lower or "hard" in v_lower:
                risk += 2
            elif "low" in v_lower or "rarely" in v_lower or "interrupted" in v_lower:
                risk += 1
    if risk >= 4:
        return models.TriageLabel.red, min(100, risk * 20)
    if risk >= 2:
        return models.TriageLabel.yellow, min(80, risk * 15)
    return models.TriageLabel.green, min(50, risk * 10)
