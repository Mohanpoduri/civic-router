"""Department classifier. Baseline = char n-gram TF-IDF + logistic regression.
Char n-grams cope with spelling variation and code-mixed text without a tokenizer, so this is a strong baseline.
The fine-tuned MuRIL / IndicBERT model should be compared against it."""
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from app.preprocess import preprocess
from app.schema import CONFIDENCE_THRESHOLD

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "models" / "dept_baseline.joblib"
SEED_PATH = ROOT / "data" / "seed_complaints.csv"


def build_pipeline() -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), sublinear_tf=True)),
        ("clf", LogisticRegression(max_iter=3000, C=20)),
    ])


def train(csv_path: Path = SEED_PATH, model_path: Path = MODEL_PATH) -> Pipeline:
    df = pd.read_csv(csv_path)
    model = build_pipeline().fit(df["text"].map(preprocess), df["department"])
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    return model


class DepartmentClassifier:
    def __init__(self, model: Pipeline | None = None):
        if model is None:
            model = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else train()
        self.model = model

    @property
    def vectorizer(self):
        return self.model.named_steps["tfidf"]

    def predict(self, text: str) -> dict:
        probs = self.model.predict_proba([preprocess(text)])[0]
        ranked = sorted(zip(self.model.classes_, probs), key=lambda p: -p[1])
        best, conf = ranked[0]
        return {
            "department": str(best),
            "confidence": round(float(conf), 3),
            "top3": [{"department": str(d), "confidence": round(float(p), 3)} for d, p in ranked[:3]],
            "needs_human": bool(conf < CONFIDENCE_THRESHOLD),
        }
