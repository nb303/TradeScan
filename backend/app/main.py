from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import sqlite3
import json
from datetime import datetime
from pathlib import Path
import uvicorn

from app.ml.classifier import analyze_listing, get_model

# App setup

app = FastAPI(
    title="TradeScan API",
    description="""
## 🦜 TradeScan — Endangered Species Listing Detection

TradeScan is an NLP-powered compliance API that detects potential illegal wildlife 
trafficking in e-commerce product listings.
    """,
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup

DB_PATH = Path(__file__).parent.parent / "tradescan.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            title TEXT,
            description TEXT,
            risk_score REAL,
            risk_level TEXT,
            recommendation TEXT,
            flagged_species TEXT,
            detection_method TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_analysis(title: str, description: str, result: dict):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO analyses 
        (timestamp, title, description, risk_score, risk_level, recommendation, flagged_species, detection_method)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.utcnow().isoformat(),
        title,
        description,
        result["risk_score"],
        result["risk_level"],
        result["recommendation"],
        json.dumps(result["flagged_species"]),
        result["detection_method"]
    ))
    conn.commit()
    conn.close()

init_db()

# ── Request/Response models ───────────────────────────────────────────────────

class ListingRequest(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=500,
        example="Authentic ivory elephant carving from Africa"
    )
    description: Optional[str] = Field(
        default="",
        max_length=5000,
        example="Hand-carved ivory piece, certified antique. Ships discreetly."
    )

class BatchListingRequest(BaseModel):
    listings: list[ListingRequest] = Field(..., max_length=50)

class SpeciesMatch(BaseModel):
    species_common: str
    species_scientific: str
    appendix: str
    trade_status: str
    matched_keyword: str

class AnalysisResponse(BaseModel):
    risk_score: float = Field(..., description="0.0 (clean) to 1.0 (highly suspicious)")
    risk_level: str = Field(..., description="CLEAN | LOW | MEDIUM | HIGH")
    recommendation: str
    flagged_species: list[SpeciesMatch]
    rule_based_score: float
    ml_score: float
    detection_method: str
    title: str
    description: str

class StatsResponse(BaseModel):
    total_analyzed: int
    high_risk: int
    medium_risk: int
    low_risk: int
    clean: int
    recent_flags: list[dict]


# API Routes

@app.get("/", tags=["Health"])
def root():
    return {
        "service": "TradeScan API",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs",
        "description": "Endangered species listing detection for e-commerce compliance"
    }

@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy", "model_loaded": True}


@app.post("/api/analyze", response_model=AnalysisResponse, tags=["Detection"])
def analyze(request: ListingRequest):
    #Analyze a single product listing for potential wildlife trafficking. 
    # Returns a risk score (0-1), risk level, matched CITES species, and recommendation.
    
    try:
        result = analyze_listing(request.title, request.description or "")
        log_analysis(request.title, request.description or "", result)
        return {
            **result,
            "title": request.title,
            "description": request.description or ""
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze/batch", tags=["Detection"])
def analyze_batch(request: BatchListingRequest):
    """
    Analyze multiple listings at once (max 50).
    Returns results sorted by risk score descending.
    """
    results = []
    for listing in request.listings:
        try:
            result = analyze_listing(listing.title, listing.description or "")
            log_analysis(listing.title, listing.description or "", result)
            results.append({
                **result,
                "title": listing.title,
                "description": listing.description or ""
            })
        except Exception as e:
            results.append({"title": listing.title, "error": str(e)})

    results.sort(key=lambda x: x.get("risk_score", 0), reverse=True)
    return {
        "count": len(results),
        "high_risk_count": sum(1 for r in results if r.get("risk_level") == "HIGH"),
        "results": results
    }


@app.get("/api/stats", response_model=StatsResponse, tags=["Analytics"])
def get_stats():
    #Returns aggregated statistics from all analyses logged in the database.
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM analyses")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM analyses WHERE risk_level = 'HIGH'")
    high = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM analyses WHERE risk_level = 'MEDIUM'")
    medium = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM analyses WHERE risk_level = 'LOW'")
    low = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM analyses WHERE risk_level = 'CLEAN'")
    clean = cursor.fetchone()[0]

    cursor.execute("""
        SELECT title, risk_score, risk_level, timestamp, flagged_species
        FROM analyses 
        WHERE risk_level IN ('HIGH', 'MEDIUM')
        ORDER BY timestamp DESC 
        LIMIT 10
    """)
    recent = cursor.fetchall()
    conn.close()

    recent_flags = [
        {
            "title": r[0],
            "risk_score": r[1],
            "risk_level": r[2],
            "timestamp": r[3],
            "flagged_species": json.loads(r[4]) if r[4] else []
        }
        for r in recent
    ]

    return {
        "total_analyzed": total,
        "high_risk": high,
        "medium_risk": medium,
        "low_risk": low,
        "clean": clean,
        "recent_flags": recent_flags
    }


@app.get("/api/species", tags=["Reference"])
def list_species(appendix: Optional[str] = None):
    #List all CITES-protected species in the database.
    #Filter by appendix: I or II

    from app.data.species_data import get_all_species
    species = get_all_species()

    if appendix:
        species = {k: v for k, v in species.items() if v["appendix"] == appendix.upper()}

    return {
        "count": len(species),
        "species": [
            {
                "name": k.replace("_", " ").title(),
                "scientific": v["scientific"],
                "appendix": v["appendix"],
                "trade_status": v["trade_status"],
                "example_products": v.get("common_products", [])
            }
            for k, v in species.items()
        ]
    }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
