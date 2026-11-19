"""Cross-validated evaluation of the baseline: macro-F1, per-class report, confusion matrix, per-language accuracy.
Usage: python -m scripts.evaluate

IMPORTANT: the seed file is tiny and hand-written. For honest numbers, hold out a test set of REAL complaints
that never appears in training or in LLM-generated data (see docs/generation_prompts.md)."""
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict

from app.classifier import SEED_PATH, build_pipeline
from app.preprocess import preprocess

df = pd.read_csv(SEED_PATH)
X, y = df["text"].map(preprocess), df["department"]
pred = cross_val_predict(build_pipeline(), X, y, cv=StratifiedKFold(n_splits=4, shuffle=True, random_state=42))

print("macro-F1:", round(f1_score(y, pred, average="macro"), 3))
print(classification_report(y, pred, zero_division=0))
labels = sorted(y.unique())
print(pd.DataFrame(confusion_matrix(y, pred, labels=labels), index=labels, columns=[l[:6] for l in labels]))
df["correct"] = pred == y
print("\naccuracy by language:\n", df.groupby("language")["correct"].mean().round(2))
