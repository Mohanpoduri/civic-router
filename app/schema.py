"""Labels and constants shared by the whole pipeline."""

DEPARTMENTS = {
    "water_supply":   "Water Supply Board",
    "roads":          "Roads & Buildings",
    "sanitation":     "Sanitation / Solid Waste",
    "drainage":       "Drainage & Sewerage",
    "electricity":    "Electricity (DISCOM)",
    "streetlights":   "Street Lighting",
    "stray_animals":  "Veterinary / Animal Control",
    "encroachment":   "Town Planning / Encroachment",
}

URGENCY_LEVELS = ["critical", "high", "medium", "low"]

# Hours within which a ticket must be acted on, per urgency level.
SLA_HOURS = {"critical": 4, "high": 24, "medium": 72, "low": 168}

# If the model is less sure than this, a human triages the ticket.
CONFIDENCE_THRESHOLD = 0.35
