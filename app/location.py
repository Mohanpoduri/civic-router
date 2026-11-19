"""Pulls ward numbers and landmarks out of a complaint. Regex + gazetteer baseline; swap for a NER model later."""
import json
import re
from pathlib import Path

GAZETTEER_PATH = Path(__file__).resolve().parent.parent / "data" / "gazetteer.json"
WARD_RE = re.compile(r"\bward\s*(?:no\.?|number)?\s*(\d{1,3})\b", re.I)
LANDMARK_RE = re.compile(
    r"\b(?:near|opposite|behind|beside|next to)\s+((?:the\s+)?[A-Za-z][A-Za-z ]{2,30}?)"
    r"(?=[,.]|\s+(?:and|is|are|has|have|there)\b|$)", re.I)


def _gazetteer() -> list[str]:
    if GAZETTEER_PATH.exists():
        return json.loads(GAZETTEER_PATH.read_text(encoding="utf-8"))
    return []


def extract_location(text: str) -> dict:
    ward = WARD_RE.search(text)
    landmark = LANDMARK_RE.search(text)
    places = [p for p in _gazetteer() if p.lower() in text.lower()]
    return {
        "ward": int(ward.group(1)) if ward else None,
        "landmark": landmark.group(1).strip() if landmark else None,
        "known_places": places,
    }
