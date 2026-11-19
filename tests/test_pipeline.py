import pytest
from fastapi.testclient import TestClient

from app.preprocess import detect_language, mask_pii
from app.urgency import score_urgency
from app.location import extract_location


def test_language_detection():
    assert detect_language("మా వీధిలో నీళ్లు రావడం లేదు") == "te"
    assert detect_language("सड़क पर गड्ढा है") == "hi"
    assert detect_language("kachra uthane wali gaadi nahi aayi") == "hi-latn"
    assert detect_language("street light veligadam ledu") == "te-latn"
    assert detect_language("Garbage is not collected") == "en"


def test_pii_masked():
    assert "9876543210" not in mask_pii("call me on 9876543210 or a@b.com")


def test_safety_words_override():
    assert score_urgency("Live wire has fallen near the park", "electricity")["level"] == "critical"
    assert score_urgency("కరెంటు తీగ తెగి రోడ్డు మీద పడింది", "electricity")["level"] == "critical"
    assert score_urgency("Footpath has a small shop", "encroachment")["level"] == "low"


def test_location():
    loc = extract_location("Pothole near the bus stand in ward 12, Kukatpally")
    assert loc["ward"] == 12 and "Kukatpally" in loc["known_places"]


@pytest.fixture(scope="module")
def client():
    from app.main import app
    return TestClient(app)


@pytest.mark.parametrize("text,dept", [
    ("There is no water in our tap since yesterday", "water_supply"),
    ("सड़क पर बहुत बड़ा गड्ढा है", "roads"),
    ("వీధి కుక్కలు పిల్లలను కరుస్తున్నాయి", "stray_animals"),
    ("street light kharab hai", "streetlights"),
])
def test_routing(client, text, dept):
    r = client.post("/complaints", json={"text": text})
    assert r.status_code == 201
    assert r.json()["department"] == dept


def test_duplicate_detection(client):
    a = client.post("/complaints", json={"text": "Garbage not collected in ward 7 for a week"}).json()
    b = client.post("/complaints", json={"text": "Garbage not collected in ward 7 for a week!"}).json()
    assert b["duplicate_of"] == a["id"]


def test_list_sorted_by_urgency(client):
    client.post("/complaints", json={"text": "Live wire fallen on the road"})
    first = client.get("/complaints").json()[0]
    assert first["urgency"]["level"] == "critical"


def test_ui_is_served(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Civic Complaint Router" in r.text
    assert client.get("/static/app.js").status_code == 200
