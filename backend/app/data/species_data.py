"""
CITES species keyword database and synthetic listing generator.
In production this pulls from the real CITES checklist CSV download.
"""

# CITES Appendix I - Fully banned from commercial trade
APPENDIX_I = {
    "elephant": {
        "scientific": "Loxodonta africana / Elephas maximus",
        "keywords": ["elephant", "ivory", "tusk", "elephant hide", "elephant leather", "elephant bone"],
        "common_products": ["ivory carving", "ivory pendant", "tusk", "ivory bracelet"]
    },
    "tiger": {
        "scientific": "Panthera tigris",
        "keywords": ["tiger", "tiger skin", "tiger fur", "tiger bone", "tiger pelt", "tiger claw"],
        "common_products": ["tiger skin rug", "tiger fur coat", "tiger bone wine"]
    },
    "rhinoceros": {
        "scientific": "Rhinocerotidae spp.",
        "keywords": ["rhino", "rhinoceros", "rhino horn", "rhino hide", "rhinoceros horn"],
        "common_products": ["rhino horn powder", "rhino horn carving", "rhino hide belt"]
    },
    "pangolin": {
        "scientific": "Manis spp.",
        "keywords": ["pangolin", "pangolin scale", "pangolin skin", "scaly anteater"],
        "common_products": ["pangolin scale", "pangolin leather", "pangolin medicine"]
    },
    "gorilla": {
        "scientific": "Gorilla gorilla",
        "keywords": ["gorilla", "great ape", "gorilla skull", "gorilla hand"],
        "common_products": ["gorilla ashtray", "gorilla trophy"]
    },
    "cheetah": {
        "scientific": "Acinonyx jubatus",
        "keywords": ["cheetah", "cheetah fur", "cheetah skin", "cheetah pelt"],
        "common_products": ["cheetah fur coat", "cheetah skin rug"]
    },
    "leopard": {
        "scientific": "Panthera pardus",
        "keywords": ["leopard", "leopard skin", "leopard fur", "leopard pelt", "leopard claw"],
        "common_products": ["leopard skin", "leopard fur stole"]
    },
    "snow_leopard": {
        "scientific": "Panthera uncia",
        "keywords": ["snow leopard", "ounce pelt", "snow leopard fur"],
        "common_products": ["snow leopard fur"]
    },
    "jaguar": {
        "scientific": "Panthera onca",
        "keywords": ["jaguar", "jaguar skin", "jaguar pelt", "jaguar fur", "jaguar tooth"],
        "common_products": ["jaguar skin rug", "jaguar tooth pendant"]
    },
    "sea_turtle": {
        "scientific": "Cheloniidae / Dermochelyidae spp.",
        "keywords": ["sea turtle", "turtle shell", "hawksbill", "tortoiseshell", "carey", "bekko"],
        "common_products": ["tortoiseshell comb", "turtle shell jewelry", "hawksbill shell"]
    },
    "shahtoosh": {
        "scientific": "Pantholops hodgsonii (Tibetan antelope)",
        "keywords": ["shahtoosh", "shatoosh", "tibetan antelope", "chiru wool", "ring shawl"],
        "common_products": ["shahtoosh shawl", "shatoosh wrap"]
    },
    "saiga": {
        "scientific": "Saiga tatarica",
        "keywords": ["saiga", "saiga horn", "saiga antelope"],
        "common_products": ["saiga horn powder"]
    },
    "orangutan": {
        "scientific": "Pongo pygmaeus",
        "keywords": ["orangutan", "orang utan", "orangutan skull"],
        "common_products": ["orangutan skull", "orangutan trophy"]
    },
    "polar_bear": {
        "scientific": "Ursus maritimus",
        "keywords": ["polar bear", "polar bear fur", "polar bear skin", "polar bear pelt", "polar bear rug"],
        "common_products": ["polar bear rug", "polar bear fur coat"]
    },
    "whale": {
        "scientific": "Balaenoptera / Megaptera spp.",
        "keywords": ["whale bone", "whalebone", "sperm whale", "ambergris", "whale ivory", "scrimshaw"],
        "common_products": ["whale bone carving", "scrimshaw", "ambergris perfume"]
    },
}

# CITES Appendix II - Regulated but trade allowed with permits
APPENDIX_II = {
    "coral": {
        "scientific": "Corallium spp.",
        "keywords": ["red coral", "precious coral", "coral skeleton", "coral branch", "black coral"],
        "common_products": ["coral jewelry", "coral carving"]
    },
    "queen_conch": {
        "scientific": "Strombus gigas",
        "keywords": ["queen conch", "conch shell", "conch pearl"],
        "common_products": ["conch shell jewelry", "conch carving"]
    },
    "mahogany": {
        "scientific": "Swietenia macrophylla",
        "keywords": ["big leaf mahogany", "bigleaf mahogany", "genuine mahogany"],
        "common_products": ["mahogany furniture", "mahogany lumber"]
    },
    "hippopotamus": {
        "scientific": "Hippopotamus amphibius",
        "keywords": ["hippo tooth", "hippo ivory", "hippopotamus ivory", "hippo tusk"],
        "common_products": ["hippo ivory carving", "hippo tooth pendant"]
    },
    "bear_bile": {
        "scientific": "Ursidae spp.",
        "keywords": ["bear bile", "bear gall", "bear gallbladder", "ursodeoxycholic wild"],
        "common_products": ["bear bile capsule", "bear gall bladder"]
    },
    "manta_ray": {
        "scientific": "Manta spp.",
        "keywords": ["manta ray gill", "manta gill plate", "manta ray fin"],
        "common_products": ["manta gill plate", "manta ray product"]
    },
    "shark_fin": {
        "scientific": "Lamna nasus / Carcharhinus spp.",
        "keywords": ["shark fin", "porbeagle fin", "oceanic whitetip fin", "hammerhead fin"],
        "common_products": ["shark fin soup", "dried shark fin"]
    },
    "alligator": {
        "scientific": "Alligator mississippiensis",
        "keywords": ["alligator skin", "gator skin", "alligator hide", "alligator leather"],
        "common_products": ["alligator leather bag", "gator skin boots"]
    },
    "python": {
        "scientific": "Python spp.",
        "keywords": ["python skin", "python leather", "burmese python skin", "reticulated python"],
        "common_products": ["python leather bag", "python skin belt"]
    },
    "cacti": {
        "scientific": "Cactaceae spp.",
        "keywords": ["saguaro cactus", "peyote", "wild cactus", "wild harvested cactus"],
        "common_products": ["wild peyote", "saguaro cactus"]
    },
}

# Evasion keywords 
EVASION_PATTERNS = [
    "exotic leather", "exotic hide", "rare animal", "wild harvested",
    "ethically sourced exotic", "antique horn", "vintage fur", "traditional medicine bone",
    "natural horn carving", "exotic scale", "rare feather", "trophy mount",
    "museum quality specimen", "taxidermy rare", "skull real", "antique ivory",
    "pre-ban ivory", "legal ivory", "certified ivory", "fossil ivory alternative"
]

def get_all_species():
    """Return flat dict of all species with appendix info."""
    all_species = {}
    for name, data in APPENDIX_I.items():
        all_species[name] = {**data, "appendix": "I", "trade_status": "Prohibited"}
    for name, data in APPENDIX_II.items():
        all_species[name] = {**data, "appendix": "II", "trade_status": "Regulated - Permit Required"}
    return all_species

def get_all_keywords():
    """Return flat list of (keyword, species_name, appendix) tuples."""
    keywords = []
    for name, data in APPENDIX_I.items():
        for kw in data["keywords"]:
            keywords.append((kw.lower(), name, "I"))
    for name, data in APPENDIX_II.items():
        for kw in data["keywords"]:
            keywords.append((kw.lower(), name, "II"))
    return keywords
