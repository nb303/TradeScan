# TradeScan

**Illegal wildlife trade detection API for e-commerce compliance**

API for detecting illegal wildlife trade in e-commerce listings

TradeScan flags risky listings using a hybrid NLP pipeline combining rule-based CITES matching with a machine learning classifier.

---
<img width="1440" height="763" alt="Screenshot 2026-04-19 at 11 49 15 PM" src="https://github.com/user-attachments/assets/aea08c84-8590-486e-adc1-4e87602f5871" />

## How it works

1. Rule-based detection

Keywords mapped to CITES Appendix I/II species
Returns species + legal status
High precision for known terms (“ivory”, “rhino horn”)
<img width="1396" height="543" alt="Screenshot 2026-04-19 at 11 53 52 PM" src="https://github.com/user-attachments/assets/8a8b204e-7fa6-4eb9-b8e4-866923188e0b" />
2. ML classifier (TF-IDF + Logistic Regression)

Trained on synthetic listings
Captures evasive phrases (“exotic horn”, “wild harvested”)

3. Hybrid scoring

Rules dominate when triggered
ML handles ambiguous cases
Safe modifiers (faux, ceramic, synthetic, cruelty-free) heavily discount false positives.


<img width="1252" height="402" alt="Screenshot 2026-04-19 at 11 54 06 PM" src="https://github.com/user-attachments/assets/a6251b01-032e-4ccd-b61a-2db9903d7f4f" />
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
