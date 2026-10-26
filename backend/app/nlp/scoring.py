"""
The candidate matching / scoring engine.

Produces a transparent, explainable score out of 100 built from five
independently-visible, configurably-weighted components (see
app.config.SCORE_WEIGHTS):

    Skill Match           50%
    Experience Match      20%
    Education Match       10%
    Project Relevance     10%
    Semantic Similarity   10%

IMPORTANT (spec section 6/17): this score measures how well a resume matches
a *job description*. It is explicitly not a judgement of the candidate's
overall quality or a hiring recommendation — see the disclaimer surfaced in
the API response and throughout the frontend.
"""
from __future__ import annotations

from app.config import SCORE_WEIGHTS
from app.nlp.similarity import get_similarity_engine
from app.nlp.skills_db import normalize_skill_list


def _skill_match(required: list[str], preferred: list[str], candidate_skills: list[str]) -> dict:
    required = normalize_skill_list(required)
    preferred = normalize_skill_list(preferred)
    candidate_set = set(normalize_skill_list(candidate_skills))

    matched_required = [s for s in required if s in candidate_set]
    matched_preferred = [s for s in preferred if s in candidate_set]
    missing_required = [s for s in required if s not in candidate_set]
    missing_preferred = [s for s in preferred if s not in candidate_set]

    if required and preferred:
        req_ratio = len(matched_required) / len(required)
        pref_ratio = len(matched_preferred) / len(preferred)
        score = req_ratio * 80 + pref_ratio * 20
    elif required:
        score = (len(matched_required) / len(required)) * 100
    elif preferred:
        score = (len(matched_preferred) / len(preferred)) * 100
    else:
        score = 100.0  # job listed no specific skills — nothing to penalize

    return {
        "score": round(min(100.0, score), 1),
        "matched": matched_required + matched_preferred,
        "missing": missing_required + missing_preferred,
    }


def _experience_match(min_experience: float, candidate_years: float | None) -> float:
    if not min_experience or min_experience <= 0:
        return 100.0
    if candidate_years is None:
        return 0.0
    if candidate_years >= min_experience:
        return 100.0
    return round(max(0.0, candidate_years / min_experience) * 100, 1)


def _education_match(required_level: int, candidate_level: int) -> float:
    if required_level <= 0:
        return 100.0
    if candidate_level >= required_level:
        return 100.0
    if candidate_level == required_level - 1:
        return 50.0  # one level below — partial credit
    return 0.0


def _project_relevance(job_text: str, projects_text: str | None, resume_text: str) -> float:
    engine = get_similarity_engine()
    basis = projects_text if projects_text and projects_text.strip() else resume_text
    return round(engine.score(job_text, basis) * 100, 1)


def _semantic_similarity(job_text: str, resume_text: str) -> float:
    engine = get_similarity_engine()
    return round(engine.score(job_text, resume_text) * 100, 1)


def _build_explanation(
    matched_skills, missing_skills, experience_score, candidate_years, min_experience,
    education_score, education_snippet, project_score,
) -> list[dict]:
    points = []

    for skill in matched_skills[:6]:
        points.append({"type": "+", "text": f"{skill.title()} found"})
    for skill in missing_skills[:6]:
        points.append({"type": "-", "text": f"{skill.title()} not found"})

    if experience_score >= 100:
        if candidate_years is not None:
            points.append({"type": "+", "text": f"{candidate_years} years relevant experience meets requirement"})
    elif candidate_years is not None:
        points.append({"type": "-", "text": f"Only {candidate_years} years experience vs. {min_experience} required"})
    else:
        points.append({"type": "-", "text": "Experience duration not detected"})

    if education_score >= 100 and education_snippet:
        points.append({"type": "+", "text": f"Education requirement met ({education_snippet[:60]})"})
    elif education_score < 100:
        points.append({"type": "-", "text": "Education requirement not clearly met"})

    if project_score >= 60:
        points.append({"type": "+", "text": "Relevant project experience found"})
    elif project_score < 30:
        points.append({"type": "-", "text": "Limited project relevance to this role"})

    return points


def compute_match(job, candidate_data: dict, resume_text: str) -> dict:
    """
    job: an app.models.job.Job ORM instance (or any object exposing the same
         attributes) with required_skills/preferred_skills already decoded
         to Python lists, plus min_experience, education_requirement_level,
         and description.
    candidate_data: dict as returned by app.nlp.extractor.parse_resume
    resume_text: full raw extracted resume text
    """
    skill_result = _skill_match(job["required_skills"], job["preferred_skills"], candidate_data["skills"])
    experience_score = _experience_match(job["min_experience"], candidate_data["experience_years"])
    education_score = _education_match(job["education_level"], candidate_data["education_level"])
    project_score = _project_relevance(job["description"], candidate_data.get("projects_text"), resume_text)
    semantic_score = _semantic_similarity(job["description"], resume_text)

    overall = (
        skill_result["score"] * SCORE_WEIGHTS["skill"]
        + experience_score * SCORE_WEIGHTS["experience"]
        + education_score * SCORE_WEIGHTS["education"]
        + project_score * SCORE_WEIGHTS["project"]
        + semantic_score * SCORE_WEIGHTS["semantic"]
    )

    explanation = _build_explanation(
        skill_result["matched"], skill_result["missing"],
        experience_score, candidate_data["experience_years"], job["min_experience"],
        education_score, candidate_data.get("education"),
        project_score,
    )

    return {
        "skill_score": skill_result["score"],
        "experience_score": experience_score,
        "education_score": education_score,
        "project_score": project_score,
        "semantic_score": semantic_score,
        "overall_score": round(overall, 1),
        "matched_skills": skill_result["matched"],
        "missing_skills": skill_result["missing"],
        "explanation": explanation,
    }
