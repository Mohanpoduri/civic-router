"""Rule-based urgency. Safety words ALWAYS win, whatever the model says."""
from app.schema import SLA_HOURS

CRITICAL_WORDS = [
    "live wire", "electric shock", "sparking", "fire", "open manhole", "manhole", "collapse", "gas leak",
    "drowning", "fallen wire", "wire has fallen", "wire has fallen",
    "तार टूट", "करंट", "आग", "ढक्कन खुला", "मैनहोल", "aag", "current lag",
    "తీగ తెగి", "కరెంట్ షాక్", "మంటలు", "మ్యాన్‌హోల్", "మ్యాన్హోల్", "మూత తెరిచి",
]
HIGH_WORDS = [
    "accident", "children", "child", "bite", "biting", "overflow", "flooding", "dirty water", "muddy", "may fall",
    "हादसे", "बच्चे", "बच्चों", "काट", "गंदा पानी", "ప్రమాదం", "పిల్లల", "కరుస్తున్న", "మురికి", "పొంగి",
    "kaat", "karistunnayi", "ghar me aa", "accident ho",
]
DEFAULT_BY_DEPT = {
    "water_supply": "medium", "roads": "medium", "sanitation": "medium", "drainage": "high",
    "electricity": "medium", "streetlights": "medium", "stray_animals": "medium", "encroachment": "low",
}


def score_urgency(text: str, department: str | None) -> dict:
    t = text.lower()
    hits = [w for w in CRITICAL_WORDS if w in t]
    if hits:
        level, reason = "critical", f"safety keyword: {hits[0]}"
    else:
        hits = [w for w in HIGH_WORDS if w in t]
        if hits:
            level, reason = "high", f"risk keyword: {hits[0]}"
        else:
            level, reason = DEFAULT_BY_DEPT.get(department or "", "medium"), "department default"
    return {"level": level, "reason": reason, "sla_hours": SLA_HOURS[level]}
