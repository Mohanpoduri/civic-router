"""Train the baseline and save it to models/. Usage: python -m scripts.train"""
from app.classifier import MODEL_PATH, SEED_PATH, train

if __name__ == "__main__":
    train()
    print(f"trained on {SEED_PATH.name} -> {MODEL_PATH}")
