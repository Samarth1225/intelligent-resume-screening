import json

from sqlalchemy.orm import Session, joinedload

from app.config import score_band
from app.models.candidate import Candidate, NOT_DETECTED
from app.models.score import CandidateScore
from app.models.job import Job
from app.services.job_service import job_to_dict


def _skills_matched_label(candidate: Candidate, score: CandidateScore | None, job_dict: dict) -> str:
    total_required = len(job_dict["required_skills"]) + len(job_dict["preferred_skills"])
    matched = len(json.loads(score.matched_skills)) if score else 0
    return f"{matched} / {total_required}" if total_required else f"{matched} / 0"


def list_candidates(
    db: Session,
    job_id: int,
    search: str | None = None,
    min_score: float | None = None,
    skills: list[str] | None = None,
    sort_by: str = "score_desc",
) -> list[dict]:
    job = db.query(Job).filter(Job.id == job_id).first()
    job_dict = job_to_dict(job) if job else {"required_skills": [], "preferred_skills": []}

    query = (
        db.query(Candidate)
        .options(joinedload(Candidate.score), joinedload(Candidate.resume))
        .filter(Candidate.job_id == job_id)
    )
    candidates = query.all()

    results = []
    for c in candidates:
        score = c.score
        overall = score.overall_score if score else 0
        candidate_skills = json.loads(c.skills or "[]")

        if search:
            haystack = f"{c.name} {c.email}".lower()
            if search.lower() not in haystack:
                continue
        if min_score is not None and overall < min_score:
            continue
        if skills:
            wanted = {s.lower() for s in skills}
            if not wanted.issubset({s.lower() for s in candidate_skills}):
                continue

        results.append({
            "id": c.id,
            "name": c.name or NOT_DETECTED,
            "email": c.email or NOT_DETECTED,
            "phone": c.phone or NOT_DETECTED,
            "skills": candidate_skills,
            "experience_years": c.experience_years,
            "overall_score": overall,
            "status_label": score_band(overall),
            "skills_matched_label": _skills_matched_label(c, score, job_dict),
            "resume_status": c.resume.status if c.resume else "unknown",
        })

    reverse = sort_by.endswith("desc")
    key = "overall_score" if "score" in sort_by else "name"
    results.sort(key=lambda r: (r[key] if r[key] is not None else -1), reverse=reverse)

    for idx, r in enumerate(results, start=1):
        r["rank"] = idx

    return results


def candidate_detail(db: Session, candidate_id: int) -> dict | None:
    candidate = (
        db.query(Candidate)
        .options(joinedload(Candidate.score), joinedload(Candidate.resume))
        .filter(Candidate.id == candidate_id)
        .first()
    )
    if not candidate:
        return None

    score = candidate.score
    explanation = json.loads(score.explanation) if score else []
    score_payload = {
        "skill_score": score.skill_score if score else 0,
        "experience_score": score.experience_score if score else 0,
        "education_score": score.education_score if score else 0,
        "project_score": score.project_score if score else 0,
        "semantic_score": score.semantic_score if score else 0,
        "overall_score": score.overall_score if score else 0,
        "matched_skills": json.loads(score.matched_skills) if score else [],
        "missing_skills": json.loads(score.missing_skills) if score else [],
        "explanation": explanation,
    }

    return {
        "id": candidate.id,
        "job_id": candidate.job_id,
        "name": candidate.name or NOT_DETECTED,
        "email": candidate.email or NOT_DETECTED,
        "phone": candidate.phone or NOT_DETECTED,
        "education": candidate.education or NOT_DETECTED,
        "experience_years": candidate.experience_years,
        "experience_text": candidate.experience_text or NOT_DETECTED,
        "skills": json.loads(candidate.skills or "[]"),
        "projects_text": candidate.projects_text or NOT_DETECTED,
        "certifications": json.loads(candidate.certifications or "[]"),
        "resume_status": candidate.resume.status if candidate.resume else "unknown",
        "resume_filename": candidate.resume.filename if candidate.resume else None,
        "created_at": candidate.created_at,
        "score": score_payload,
    }
