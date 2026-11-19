"""Duplicate detection. TF-IDF cosine baseline; replace with multilingual-e5 + pgvector for production."""
from sklearn.metrics.pairwise import cosine_similarity

DUP_THRESHOLD = 0.75


class DuplicateIndex:
    def __init__(self, vectorizer):
        self.vectorizer = vectorizer
        self.items: list[dict] = []

    def find(self, text: str, department: str, ward: int | None):
        """Return (id_of_original, similarity). Only compares within the same department (and ward if known)."""
        vec = self.vectorizer.transform([text])
        best_id, best_sim = None, 0.0
        for it in self.items:
            if it["department"] != department or (ward and it["ward"] and ward != it["ward"]):
                continue
            sim = float(cosine_similarity(vec, it["vec"])[0][0])
            if sim > best_sim:
                best_id, best_sim = it["id"], sim
        return (best_id if best_sim >= DUP_THRESHOLD else None), round(best_sim, 3)

    def add(self, ticket_id: int, text: str, department: str, ward: int | None):
        self.items.append({"id": ticket_id, "department": department, "ward": ward,
                           "vec": self.vectorizer.transform([text])})
