"""Cleaning, PII masking and language/script detection."""
import re
import unicodedata

PHONE_RE = re.compile(r"(?<!\d)(?:\+?91[\s-]?)?[6-9]\d{9}(?!\d)")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")

# Tiny word lists for romanised (Latin-script) Hindi / Telugu. Replace with fastText lid later.
HI_LATN = {"hai", "hain", "nahi", "nahin", "kar", "raha", "rahi", "rahe", "mein", "me", "par", "pe", "ka", "ki",
           "ke", "se", "aur", "bahut", "din", "paani", "kachra", "naali", "kharab", "andhera", "kai"}
TE_LATN = {"ledu", "undi", "unnayi", "lo", "meeda", "maa", "neellu", "chala", "avthundi", "ayyindi", "nundi",
           "raavatledu", "veligadam", "pettaru", "karistunnayi", "ekkuva", "poyindi", "gantalu", "vaaram"}


def mask_pii(text: str) -> str:
    text = EMAIL_RE.sub("<EMAIL>", text)
    return PHONE_RE.sub("<PHONE>", text)


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", text).strip()


def detect_language(text: str) -> str:
    """Returns: te, hi, en, te-latn, hi-latn. Script first, then word lists for Latin text."""
    telugu = sum("\u0c00" <= ch <= "\u0c7f" for ch in text)
    devanagari = sum("\u0900" <= ch <= "\u097f" for ch in text)
    latin = sum(ch.isascii() and ch.isalpha() for ch in text)
    if telugu > max(devanagari, latin):
        return "te"
    if devanagari > max(telugu, latin):
        return "hi"
    words = set(re.findall(r"[a-z]+", text.lower()))
    hi, te = len(words & HI_LATN), len(words & TE_LATN)
    if te > hi and te >= 1:
        return "te-latn"
    if hi > te and hi >= 1:
        return "hi-latn"
    return "en"


def preprocess(text: str) -> str:
    return normalize(mask_pii(text))
