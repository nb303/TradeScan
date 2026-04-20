# TradeScan

**Illegal wildlife trade detection API for e-commerce compliance**

API for detecting illegal wildlife trade in e-commerce listings

TradeScan flags risky listings using a hybrid NLP pipeline combining rule-based CITES matching with a machine learning classifier.

---

## How it works

1. Rule-based detection

Keywords mapped to CITES Appendix I/II species
Returns species + legal status
High precision for known terms (“ivory”, “rhino horn”)

2. ML classifier (TF-IDF + Logistic Regression)

Trained on synthetic listings
Captures evasive phrases (“exotic horn”, “wild harvested”)

3. Hybrid scoring

Rules dominate when triggered
ML handles ambiguous cases

Safe modifiers (faux, ceramic, synthetic, cruelty-free) heavily discount false positives.

---

## Risk levels

| Level  | Score    | Action                              |
|--------|----------|-------------------------------------|
| HIGH   | ≥ 0.75   | Block — likely CITES violation      |
| MEDIUM | 0.45–0.74| Flag for manual review              |
| LOW    | 0.20–0.44| Publish with monitoring             |
| CLEAN  | < 0.20   | No issues detected                  |

---

## Data sources

- [CITES Species+ database](https://speciesplus.net/) — official species listings
- [CITES Trade Database](https://trade.cites.org/) — historical trade data
- [WWF Wildlife Crime](https://www.worldwildlife.org/initiatives/stopping-wildlife-crime) — threat context

---

## License

MIT
