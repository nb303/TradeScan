import re
import pickle
import os
import sys
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

sys.path.append(str(Path(__file__).parent.parent))

from data.species_data import get_all_keywords, get_all_species, EVASION_PATTERNS
from data.generate_training_data import generate_dataset

MODEL_PATH = Path(__file__).parent / "model.pkl"
KEYWORD_WEIGHT = 0.75  # weight to rule-based layer
ML_WEIGHT = 0.25       # weight to ML layer

# negation patterns
SAFE_MODIFIERS = [
    "faux", "fake", "synthetic", "artificial", "replica", "imitation", "vegan",
    "ceramic", "resin", "plastic", "rubber", "polyester", "cotton", "printed",
    "pattern", "stuffed", "plush", "toy", "figurine", "illustration",
    "photograph", "photo", "picture", "painting", "drawing", "embroidered",
    "carved wood", "mango wood", "bamboo", "recycled", "lab-grown", "cruelty-free",
    "cruelty free", "no animals", "100% synthetic", "100 percent synthetic",
]


# Rule-based layer 

def rule_based_score(text: str) -> tuple[float, list[dict]]:
    """
    Scan text for CITES species keywords.
    Returns (score 0-1, list of matched species info)
    """
    text_lower = text.lower()
    matched = []
    all_keywords = get_all_keywords()
    all_species = get_all_species()

    # Check for safe modifiers (vegan)
    has_safe_modifier = any(mod in text_lower for mod in SAFE_MODIFIERS)

    matched_species = set()
    for keyword, species_name, appendix in all_keywords:
        if keyword in text_lower and species_name not in matched_species:
            matched_species.add(species_name)
            species_data = all_species[species_name]
            matched.append({
                "species_common": species_name.replace("_", " ").title(),
                "species_scientific": species_data["scientific"],
                "appendix": appendix,
                "trade_status": species_data["trade_status"],
                "matched_keyword": keyword
            })

    evasion_count = sum(1 for pattern in EVASION_PATTERNS if pattern in text_lower)

    if not matched and evasion_count == 0:
        return 0.0, []

    base_score = min(1.0, len(matched) * 0.55 + evasion_count * 0.15)

    # Appendix I hits are more severe — automatically HIGH
    appendix_i_count = sum(1 for m in matched if m["appendix"] == "I")
    if appendix_i_count > 0:
        base_score = max(base_score, 0.82)
    if has_safe_modifier and evasion_count == 0:
        base_score *= 0.15  # nearly zero — don't flag faux/ceramic/plush items

    return min(1.0, base_score), matched if not has_safe_modifier else []


# ML layer 

def train_model():
    #Train TF-IDF + LogisticRegression pipeline on synthetic data.
    print("Generating training data...")
    dataset = generate_dataset(n_positive=400, n_negative=500)

    texts = [f"{d['title']} {d['description']}" for d in dataset]
    labels = [d["label"] for d in dataset]

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),   
            max_features=8000,
            sublinear_tf=True,    
            min_df=2,
        )),
        ("clf", LogisticRegression(
            C=1.0,
            class_weight="balanced",
            max_iter=1000,
            random_state=42,
        ))
    ])

    print("Training model...")
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    print("\n── Model Performance ──")
    print(classification_report(y_test, y_pred, target_names=["Clean", "Flagged"]))

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(pipeline, f)
    print(f"Model saved to {MODEL_PATH}")

    return pipeline


def load_model():
    if not MODEL_PATH.exists():
        print("No model found — training now...")
        return train_model()

    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


# Combined inference of rules and ML

_model = None

def get_model():
    global _model
    if _model is None:
        _model = load_model()
    return _model


def analyze_listing(title: str, description: str = "") -> dict:
    """
    Main inference function.
    Returns full analysis result for a product listing.
    """
    full_text = f"{title} {description}".strip()

    # Layer 1 — Rule-based
    rule_score, matched_species = rule_based_score(full_text)

    # Layer 2 — ML
    model = get_model()
    ml_proba = model.predict_proba([full_text])[0][1]  # probability of class=1 (flagged)

    # Blend scores
    if rule_score > 0:
        # If rules fired, weight them more heavily
        final_score = (KEYWORD_WEIGHT * rule_score) + (ML_WEIGHT * ml_proba)
    else:
        # No keyword match rely on ML 
        final_score = ml_proba

    final_score = round(float(np.clip(final_score, 0.0, 1.0)), 4)

    # Risk level
    if final_score >= 0.70:
        risk_level = "HIGH"
        recommendation = "Block listing — likely violates CITES regulations"
    elif final_score >= 0.42:
        risk_level = "MEDIUM"
        recommendation = "Flag for manual review before publishing"
    elif final_score >= 0.20:
        risk_level = "LOW"
        recommendation = "Publish with monitoring"
    else:
        risk_level = "CLEAN"
        recommendation = "No issues detected"

    return {
        "risk_score": final_score,
        "risk_level": risk_level,
        "recommendation": recommendation,
        "flagged_species": matched_species,
        "rule_based_score": round(rule_score, 4),
        "ml_score": round(float(ml_proba), 4),
        "detection_method": "hybrid" if rule_score > 0 and ml_proba > 0.3 else
                            "rule_based" if rule_score > 0 else "ml_only"
    }

def evaluate_full_system(test_cases):
    from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix
    
    y_true = []
    y_pred = []
    
    for title, description, label in test_cases:
        result = analyze_listing(title, description)
        predicted = 1 if result["risk_level"] in ["HIGH", "MEDIUM"] else 0
        y_true.append(label)
        y_pred.append(predicted)
        status = "✅" if predicted == label else "❌"
        print(f"{status} [{result['risk_level']:6}] {result['risk_score']:.2f} | {title}")
    
    print("\n── Full System Metrics ──")
    print(f"Precision: {precision_score(y_true, y_pred):.2f}")
    print(f"Recall:    {recall_score(y_true, y_pred):.2f}")
    print(f"F1:        {f1_score(y_true, y_pred):.2f}")
    print(f"Confusion matrix:\n{confusion_matrix(y_true, y_pred)}")


if __name__ == "__main__":
    train_model()
    
    # 1 = flagged, 0 = clean
    test_cases = [
        # Clear positives — should be HIGH/MEDIUM
        ("Authentic ivory elephant carving", "Hand-carved from Africa, antique certified, ships discreetly", 1),
        ("Rhino horn powder capsules", "Traditional medicine, 100% authentic wild sourced", 1),
        ("Pangolin scale medicine", "Ground pangolin scales encapsulated, wild harvested", 1),
        ("Shahtoosh shawl genuine", "Ring shawl tibetan antelope wild harvested chiru wool", 1),
        ("Leopard skin rug", "Real leopard pelt, ethically hunted trophy", 1),
        ("Tiger bone wine", "Traditional remedy made from tiger bones", 1),
        ("Whale bone carving antique", "Sperm whale ivory scrimshaw pre-ban", 1),
        ("Polar bear fur coat", "Real polar bear pelt, legally obtained Canada", 1),
        # Evasive positives — tricky, no species named directly
        ("Exotic horn carving", "Rare natural horn ethically sourced wild animal", 1),
        ("Antique horn medicine", "Traditional remedy ground horn powder wild sourced", 1),
        ("Rare scale capsules", "Wild harvested exotic animal scale traditional medicine", 1),
        ("Trophy mount museum quality", "Real animal skull legally imported documentation included", 1),
        ("Exotic leather wallet", "Wild animal hide rare material ships discreetly", 1),
        # Clear negatives — should be CLEAN
        ("Faux fur leopard jacket", "100% polyester faux fur no animals harmed cruelty free", 0),
        ("Ceramic elephant figurine", "Handmade ceramic 100% synthetic kiln fired", 0),
        ("Bamboo cutting board", "Eco friendly sustainably grown bamboo", 0),
        ("Vegan leather handbag", "PU leather cruelty free synthetic no animals", 0),
        ("Stuffed panda plush toy", "Polyester stuffed animal toy", 0),
        ("Lab grown diamond ring", "Ethical lab created diamond conflict free", 0),
        ("Organic cotton safari shirt", "100% cotton no animal products", 0),
        # Tricky negatives — could confuse the model
        ("Elephant print cushion", "Decorative cushion with elephant illustration embroidered", 0),
        ("Shark tooth necklace replica", "Resin cast replica shark tooth no real teeth used", 0),
        ("Ivory white ceramic vase", "Pure white ceramic vase no animal products", 0),
        ("Tiger stripe yoga mat", "Non slip TPE mat with tiger pattern cruelty free", 0),
        ("Coral pink dress", "Cotton dress coral pink color no real coral", 0),
    ]
    
    print("\n── Hand-crafted Adversarial Eval ──")
    evaluate_full_system(test_cases)