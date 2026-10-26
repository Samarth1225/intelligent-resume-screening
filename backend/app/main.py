import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS, EDUCATION_REQUIREMENT_OPTIONS, SCORE_WEIGHTS
from app.database import Base, engine
from app import models  # noqa: F401 - ensures models are registered on Base
from app.routes import auth, jobs, candidates

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Intelligent Resume Screening & Candidate Ranking System",
    description="AI-assisted recruitment API: job-description matching, resume parsing, and explainable candidate ranking.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(candidates.router)


@app.get("/", tags=["health"])
def root():
    return {
        "app": "Intelligent Resume Screening & Candidate Ranking System",
        "status": "ok",
        "disclaimer": (
            "This system provides an automated job-description matching analysis "
            "and is intended to assist, not replace, human recruitment decisions."
        ),
    }


@app.get("/api/health", tags=["health"])
def health():
    return {"status": "ok"}


@app.get("/api/meta", tags=["health"])
def meta():
    """Exposes config the frontend needs to render forms (education options,
    score weights for the "how scoring works" tooltip) without hardcoding
    them twice."""
    return {
        "education_requirement_options": EDUCATION_REQUIREMENT_OPTIONS,
        "score_weights": SCORE_WEIGHTS,
    }
