# Civic Complaint Router

Routes citizen complaints written in English, Telugu, Hindi and romanised Telugu/Hindi (code-mixed) to the right
municipal department, scores urgency, extracts the location and flags duplicates.

## Pipeline
`text -> mask PII -> language detect -> department classifier -> urgency rules -> location extraction -> dedup -> ticket + SLA`

## Run
```bash
pip install -r requirements-dev.txt
python -m scripts.train          # trains the TF-IDF baseline on data/seed_complaints.csv
python -m scripts.evaluate       # cross-validated metrics
pytest                           # unit + API tests
uvicorn app.main:app --reload    # http://localhost:8000/docs
```
```bash
curl -X POST localhost:8000/complaints -H 'content-type: application/json' \
  -d '{"text": "Live wire has fallen near the park in ward 12"}'
```

## Status
| Piece | State |
|---|---|
| Preprocess, language ID, PII masking | done (rule-based) |
| Department classifier | baseline only; **seed data is too small, see below** |
| Urgency | rules with safety-word override |
| Location | regex + gazetteer |
| Dedup | TF-IDF cosine |
| Storage | in-memory (move to PostgreSQL) |

## Known limitation: data
The 66-row seed file is only there to make the pipeline run. Cross-validated macro-F1 on it is about 0.17, close to
chance for 8 classes, because there are only 1 to 2 examples per class per language. Realistic numbers need
1,500+ labelled examples (see `docs/generation_prompts.md`, `docs/label_schema.md`).

## Roadmap
1. Build the dataset (real + synthetic, with a real-only test set)
2. Fine-tune MuRIL / IndicBERT and compare with the baseline
3. NER model for locations
4. multilingual-e5 embeddings + pgvector for dedup
5. PostgreSQL, auth, Telegram/WhatsApp bot, dashboard
6. Deploy on AWS (ECS or Lambda, RDS, CloudWatch)
