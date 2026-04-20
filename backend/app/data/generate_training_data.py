"""
Generates synthetic product listings for training the classifier.
Mix of flagged (positive) and clean (negative) examples.
"""

import random
import json

# POSITIVE listing templates 

FLAGGED_TEMPLATES = [
    #Direct
    "Authentic {product} handcrafted by local artisans",
    "Vintage {product} in excellent condition, antique certified",
    "Rare {product} sourced ethically from sustainable suppliers",
    "Beautiful {product} perfect for collectors",
    "Genuine {product} — museum quality specimen",
    "Traditional {product} used in ceremonial practices",
    "Hand-carved {product} one of a kind piece",
    "Natural {product} direct from Africa",
    "Exotic {product} — pre-ban certified",
    "{product} — authentic and legal, documentation available",
    # Evasive
    "Exotic leather {category} — unique and rare material",
    "Antique horn carving — {category} style, pre-ban era",
    "Traditional medicine — {product} widely used in Asia",
    "Taxidermy {species} — legally obtained trophy",
    "Ethically sourced {product} from sustainable harvest",
    "Rare natural {category} — wild harvested and authentic",
    "Vintage {product} — antique certificate included",
    "Exotic {category} product from South East Asia",
    "Trophy mount {species} — legally imported with paperwork",
]

FLAGGED_DESCRIPTIONS = [
    "This {product} has been in our family for generations. Sourced directly from {origin}, "
    "this piece carries cultural significance and is perfect for serious collectors.",

    "Authentic {product} with documentation of origin. This is a rare find — "
    "we guarantee the quality and authenticity. Ships discreetly.",

    "Traditional {product} widely used in Chinese medicine practices. "
    "Known for its powerful properties. Discreet packaging available.",

    "Museum-grade {product} with certificate of authenticity. "
    "Pre-dates CITES regulations. Legal to own and display.",

    "Wild-harvested {product} from sustainable local hunters in {origin}. "
    "Ethically obtained with full documentation.",

    "This exotic {category} piece is one-of-a-kind. The material is incredibly rare "
    "and sourced from {origin}. Perfect as a statement piece or collector's item.",
]

SPECIES_PRODUCTS = {
    "ivory": ("elephant", "Africa", "decorative", ["ivory carving", "ivory pendant", "ivory figurine", "ivory chess set", "ivory bangle"]),
    "rhino horn": ("rhinoceros", "Sub-Saharan Africa", "medicine/decor", ["rhino horn powder", "rhino horn cup", "rhino horn carving", "rhino horn bead"]),
    "tiger bone": ("tiger", "Southeast Asia", "medicine", ["tiger bone wine", "tiger bone pill", "tiger bone plaster", "tiger bone paste"]),
    "pangolin scale": ("pangolin", "Asia/Africa", "medicine", ["pangolin scale capsule", "pangolin scale powder", "pangolin armor piece"]),
    "tortoiseshell": ("sea turtle", "tropical oceans", "decorative", ["tortoiseshell comb", "tortoiseshell frame", "tortoiseshell jewelry", "hawksbill shell"]),
    "shahtoosh": ("tibetan antelope", "Tibet", "fashion", ["shahtoosh shawl", "shahtoosh wrap", "ring shawl", "chiru wool scarf"]),
    "bear bile": ("bear", "Asia", "medicine", ["bear bile capsule", "bear gall powder", "bear bile tonic"]),
    "shark fin": ("shark", "Pacific Ocean", "food", ["dried shark fin", "shark fin soup ingredient", "shark fin whole"]),
    "coral": ("coral", "tropical reefs", "decorative", ["red coral bracelet", "coral branch", "black coral necklace", "coral carving"]),
    "polar bear fur": ("polar bear", "Arctic", "fashion/decor", ["polar bear rug", "polar bear fur throw", "polar bear skin"]),
    "leopard skin": ("leopard", "Africa", "fashion/decor", ["leopard skin rug", "leopard fur coat", "leopard pelt", "leopard skin hat"]),
    "whale bone": ("whale", "oceans", "decorative", ["whale bone carving", "scrimshaw", "whale tooth", "sperm whale ivory"]),
}

# gNEGATIVE (clean) listing templates 

CLEAN_PRODUCTS = [
    ("Handmade ceramic elephant figurine", "Beautifully crafted ceramic elephant, kiln-fired and hand-painted by local artists. 100% synthetic materials."),
    ("Faux fur leopard print jacket", "Stunning faux fur coat with bold leopard print pattern. 100% polyester — no animals harmed."),
    ("Vegan leather handbag", "Premium vegan leather handbag. PU leather exterior, fully cruelty-free and sustainable."),
    ("Wooden elephant sculpture", "Hand-carved mango wood elephant sculpture. Sustainably sourced wood from managed forests."),
    ("Tiger print yoga mat", "Non-slip yoga mat with tiger stripe design. Eco-friendly TPE material."),
    ("Synthetic coral reef décor", "Aquarium decoration piece — realistic synthetic coral. Safe for fish, no real coral used."),
    ("Shark tooth necklace (replica)", "Resin-cast shark tooth replica necklace. No real shark teeth — ethically made."),
    ("Faux python print wallet", "Faux python embossed wallet. Synthetic material only, no snakeskin used."),
    ("Cotton safari shirt", "Classic khaki safari shirt, 100% cotton. Perfect for outdoor adventures."),
    ("Stuffed animal panda plush", "Super soft giant panda plush toy. Polyester fill, no animal products."),
    ("Organic bamboo cutting board", "Eco-friendly bamboo cutting board. Sustainably grown and harvested bamboo."),
    ("Recycled rubber phone case", "Phone case made from recycled rubber. Durable, sustainable, cruelty-free."),
    ("Botanical perfume — wild jasmine", "All-natural botanical perfume. Plant-derived ingredients only, no animal musk."),
    ("Lab-grown diamond ring", "Ethically created lab-grown diamond. Conflict-free, no mining required."),
    ("Merino wool scarf (certified)", "Certified responsible wool scarf. ZQ Merino certified — humane farming practices."),
    ("Printed wildlife photography book", "Coffee table book featuring stunning wildlife photography. 100% paper product."),
    ("Conservation donation gift card", "Give the gift of conservation. Donation goes directly to WWF wildlife programs."),
    ("Beeswax candles — local honey farm", "Natural beeswax candles from local sustainable apiaries. Warm amber scent."),
    ("Embroidered linen elephant cushion", "Decorative cushion with hand-embroidered elephant motif. 100% linen cover."),
    ("Aloe vera skincare set", "Natural skincare set. Aloe vera and plant extracts. Vegan and cruelty-free certified."),
]


def generate_positive_listing():
    """Generate a flagged listing."""
    species_key = random.choice(list(SPECIES_PRODUCTS.keys()))
    species_name, origin, category, products = SPECIES_PRODUCTS[species_key]
    product = random.choice(products)

    title_template = random.choice(FLAGGED_TEMPLATES)
    title = title_template.format(
        product=product,
        species=species_name,
        category=category
    )

    desc_template = random.choice(FLAGGED_DESCRIPTIONS)
    description = desc_template.format(
        product=product,
        species=species_name,
        origin=origin,
        category=category
    )

    return {
        "title": title,
        "description": description,
        "label": 1,
        "species_hint": species_name,
        "appendix_hint": "I" if species_key in ["ivory", "rhino horn", "tiger bone", "pangolin scale", "tortoiseshell", "shahtoosh", "polar bear fur", "leopard skin", "whale bone"] else "II"
    }


def generate_negative_listing():
    """Generate a clean (safe) listing."""
    title, description = random.choice(CLEAN_PRODUCTS)
    # Add some variation
    adjectives = ["Premium", "Handcrafted", "Beautiful", "Authentic", "Sustainable", "Eco-friendly", ""]
    adj = random.choice(adjectives)
    if adj:
        title = f"{adj} {title}"

    return {
        "title": title,
        "description": description,
        "label": 0,
        "species_hint": None,
        "appendix_hint": None
    }


def generate_dataset(n_positive=400, n_negative=500):
    """Generate full training dataset."""
    dataset = []

    for _ in range(n_positive):
        dataset.append(generate_positive_listing())

    for _ in range(n_negative):
        dataset.append(generate_negative_listing())

    random.shuffle(dataset)
    return dataset


if __name__ == "__main__":
    data = generate_dataset()
    with open("training_data.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {len(data)} listings ({sum(d['label'] for d in data)} flagged, {sum(1-d['label'] for d in data)} clean)")
