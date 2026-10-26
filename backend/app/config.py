"""
Central configuration for the Intelligent Resume Screening system.

Keeping the scoring weights, education-level ranking, and file rules here
(instead of scattered across modules) is what makes the matching algorithm
"configurable" as required by the project spec — a recruiter-facing admin
screen or a config file reload could change these without touching the
scoring logic itself.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'resume_screening.db'}")

# ---------------------------------------------------------------------------
# File uploads
# ---------------------------------------------------------------------------
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE_MB = 10

# ---------------------------------------------------------------------------
# Candidate matching score weights (must sum to 1.0)
# Skill Match 50% / Experience 20% / Education 10% / Project 10% / Semantic 10%
# ---------------------------------------------------------------------------
SCORE_WEIGHTS = {
    "skill": 0.50,
    "experience": 0.20,
    "education": 0.10,
    "project": 0.10,
    "semantic": 0.10,
}
assert abs(sum(SCORE_WEIGHTS.values()) - 1.0) < 1e-6, "SCORE_WEIGHTS must sum to 1.0"

# Score band used for the "Status" column / badge shown on the dashboard
SCORE_BANDS = [
    (80, "Strong"),
    (65, "Good"),
    (50, "Fair"),
    (0, "Weak"),
]

def score_band(score: float) -> str:
    for threshold, label in SCORE_BANDS:
        if score >= threshold:
            return label
    return "Weak"

# ---------------------------------------------------------------------------
# Education levels — used to compare a candidate's highest qualification
# against a job's education requirement on a simple ordinal scale.
# ---------------------------------------------------------------------------
EDUCATION_LEVELS = {
    "any": 0,
    "high school": 1,
    "diploma": 2,
    "associate": 2,
    "bachelor": 3,
    "master": 4,
    "phd": 5,
}

# Options exposed to the frontend when a recruiter creates a job
EDUCATION_REQUIREMENT_OPTIONS = ["Any", "Diploma", "Bachelor's", "Master's", "PhD"]

def normalize_education_requirement(value: str) -> int:
    """Map a job's education requirement string to an ordinal level."""
    if not value:
        return EDUCATION_LEVELS["any"]
    v = value.strip().lower()
    if "phd" in v or "doctor" in v:
        return EDUCATION_LEVELS["phd"]
    if "master" in v or v in ("m.tech", "msc", "mca", "mba", "ma"):
        return EDUCATION_LEVELS["master"]
    if "bachelor" in v or v in ("b.tech", "be", "bsc", "bca", "b.com", "ba"):
        return EDUCATION_LEVELS["bachelor"]
    if "diploma" in v or "associate" in v:
        return EDUCATION_LEVELS["diploma"]
    if "high school" in v or "hsc" in v or "12th" in v:
        return EDUCATION_LEVELS["high school"]
    return EDUCATION_LEVELS["any"]

# ---------------------------------------------------------------------------
# Demo authentication (MVP only — NOT for production use)
# ---------------------------------------------------------------------------
DEMO_USER_EMAIL = os.getenv("DEMO_USER_EMAIL", "demo@resumescreen.ai")
DEMO_USER_PASSWORD = os.getenv("DEMO_USER_PASSWORD", "demo1234")
DEMO_TOKEN = os.getenv("DEMO_TOKEN", "demo-static-token-irscs")

# ---------------------------------------------------------------------------
# CORS — allow the local Vite dev server (and any origin in dev mode)
# ---------------------------------------------------------------------------
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
