# TradeScan 🦚🦜🐒🦉

**Wildlife trade compliance API for e-commerce listings**

TradeScan is an NLP-powered REST API that detects potential illegal wildlife trafficking in product listings at submission time. Once a listing title and description is submitted — TradeScan returns a risk score, matched CITES species, and a publish recommendation before the listing goes live.

------
<img width="1440" height="763" alt="Screenshot 2026-04-19 at 11 49 15 PM" src="https://github.com/user-attachments/assets/aea08c84-8590-486e-adc1-4e87602f5871" />

## How it works

1. Rule-based detection

Scans listing text against a keyword database derived from CITES Appendix I/II 
species. Direct hits ("ivory", "rhino horn", "pangolin scale") map to scientific 
name, appendix classification, and trade status. Appendix I hits are automatically 
high severity.
<img width="1396" height="543" alt="Screenshot 2026-04-19 at 11 53 52 PM" src="https://github.com/user-attachments/assets/8a8b204e-7fa6-4eb9-b8e4-866923188e0b" />

2. ML classifier (TF-IDF + Logistic Regression)

Catches evasive listings where sellers obscure the species. TF-IDF vectorizes listing text into weighted term frequencies using single and multi-word phrases. Logistic regression with `class_weight='balanced'` classifies against a decision boundary trained on 900 synthetic merchant listings.Captures signals like "wild harvested exotic horn" 
without a species ever being named.

3. Hybrid scoring

Rule-based score weighted at 75%, ML at 25% when rules fire. When no keyword 
matches, ML score is used alone. Safe modifiers (faux, ceramic, synthetic, 
cruelty-free) discount false positives from fashion and decor items. On a 
hand-crafted adversarial test set, the full pipeline achieves 1.00 precision 
and 0.82 F1 score.


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
- [WWF Wildlife Crime](https://www.worldwildlife.org/our-work/wildlife/wildlife-crime/stop-illegal-wildlife-trade-online/coalition-to-end-wildlife-trafficking-online/) — threat context

---

## License

MIT
