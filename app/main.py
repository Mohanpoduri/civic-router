"""FastAPI service. Serves the web UI at / and the JSON API under /complaints.
Storage is in-memory for now; swap TICKETS for PostgreSQL (SQLAlchemy) next."""
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.classifier import DepartmentClassifier
from app.dedup import DuplicateIndex
from app.location import extract_location
from app.preprocess import detect_language, preprocess
from app.schema import DEPARTMENTS
from app.urgency import score_urgency

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Civic Complaint Router", version="0.2.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

classifier = DepartmentClassifier()
dedup = DuplicateIndex(classifier.vectorizer)
TICKETS: dict[int, dict] = {}
URGENCY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


class ComplaintIn(BaseModel):
    text: str = Field(min_length=3, max_length=2000)
    source: str = "web"


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health():
    return {"status": "ok", "tickets": len(TICKETS)}


@app.get("/departments")
def departments():
    return DEPARTMENTS


@app.post("/complaints", status_code=201)
def create_complaint(body: ComplaintIn):
    clean = preprocess(body.text)
    language = detect_language(clean)
    pred = classifier.predict(clean)
    dept = pred["department"]
    urgency = score_urgency(clean, dept)
    location = extract_location(clean)
    dup_id, sim = dedup.find(clean, dept, location["ward"])

    ticket_id = len(TICKETS) + 1
    now = datetime.now(timezone.utc)
    ticket = {
        "id": ticket_id, "text": clean, "source": body.source, "language": language,
        "department": dept, "department_name": DEPARTMENTS[dept], "confidence": pred["confidence"],
        "top3": pred["top3"], "needs_human": pred["needs_human"], "urgency": urgency, "location": location,
        "duplicate_of": dup_id, "duplicate_similarity": sim,
        "status": "needs_triage" if pred["needs_human"] else "routed",
        "created_at": now.isoformat(), "sla_due": (now + timedelta(hours=urgency["sla_hours"])).isoformat(),
    }
    TICKETS[ticket_id] = ticket
    if dup_id is None:
        dedup.add(ticket_id, clean, dept, location["ward"])
    return ticket


@app.get("/complaints/{ticket_id}")
def get_complaint(ticket_id: int):
    if ticket_id not in TICKETS:
        raise HTTPException(404, "ticket not found")
    return TICKETS[ticket_id]


@app.get("/complaints")
def list_complaints(department: str | None = None, urgency: str | None = None):
    out = list(TICKETS.values())
    if department:
        out = [t for t in out if t["department"] == department]
    if urgency:
        out = [t for t in out if t["urgency"]["level"] == urgency]
    return sorted(out, key=lambda t: (URGENCY_ORDER[t["urgency"]["level"]], t["created_at"]))
