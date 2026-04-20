# TradeScan🦅

**Endangered species listing detection API for e-commerce compliance**

TradeScan is an NLP-powered compliance tool that detects potential illegal wildlife trafficking in product listings. It uses a hybrid detection approach — CITES species keyword matching combined with a machine learning classifier — to flag suspicious listings before they go live.

Built as a reference implementation for e-commerce platform trust & safety teams.

---

## How it works

### Two-layer detection pipeline

**Layer 1 — Rule-based CITES matching**
- Maintains a keyword database derived from the CITES species checklist
- Covers Appendix I (fully prohibited) and Appendix II (permit required) species
- Matches species names, common names, product types, and known evasion phrases
- Returns matched species with scientific name, appendix classification, and trade status

**Layer 2 — TF-IDF + Logistic Regression classifier**
- Trained on 900 synthetic product listings (flagged + clean)
- TF-IDF vectorizer with bigrams captures phrases like "wild harvested" and "ships discreetly"
- Logistic Regression with `class_weight='balanced'` handles imbalanced data
- Catches evasive listings that don't directly name a species

**Score blending**
```
if rule layer fired:
    final_score = 0.65 * rule_score + 0.35 * ml_score
else:
    final_score = ml_score   # rely on ML for evasive cases
```

Safe modifiers (faux, ceramic, synthetic, cruelty-free...) heavily discount false positives.

---

## Risk levels

| Level  | Score    | Action                              |
|--------|----------|-------------------------------------|
| HIGH   | ≥ 0.75   | Block — likely CITES violation      |
| MEDIUM | 0.45–0.74| Flag for manual review              |
| LOW    | 0.20–0.44| Publish with monitoring             |
| CLEAN  | < 0.20   | No issues detected                  |

---

## Quickstart

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Train the model (runs automatically on first API call too)
python -m app.ml.classifier

# Start the API
uvicorn app.main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs  (Swagger UI)
```

### Frontend

```bash
cd frontend
npm install
REACT_APP_API_URL=http://localhost:8000 npm start
# → http://localhost:3000
```

---

## Deployment (Railway)

1. Push repo to GitHub
2. Create new project on [Railway](https://railway.app)
3. Connect your GitHub repo
4. Railway auto-detects the `Procfile` and deploys
5. Set env var `PORT` (Railway sets this automatically)
6. Your API is live at `https://yourapp.up.railway.app`

---


**Why two layers instead of just ML?**
The rule-based layer is deterministic and explainable — critical for a compliance tool where you need to cite the exact CITES regulation. The ML layer handles evasive language that doesn't directly name a species. Blending both gives you recall on clear-cut cases and precision on ambiguous ones.

---

## Limitations and future work

- Training data is synthetic — production would require real labeled e-commerce listings
- No image analysis — many listings hide trafficking in product photos
- CITES database coverage is incomplete — a full implementation would import the official [CITES checklist](https://checklist.cites.org/) CSV (~38,000 species)
- False positive rate on exotic-themed fashion (leopard print, faux fur) is managed by safe modifiers but not zero
- Future: fine-tune a small BERT model on real labeled data for improved recall on evasive listings

---

## Data sources

- [CITES Species+ database](https://speciesplus.net/) — official species listings
- [CITES Trade Database](https://trade.cites.org/) — historical trade data
- [WWF Wildlife Crime](https://www.worldwildlife.org/initiatives/stopping-wildlife-crime) — threat context

---

## License

MIT
