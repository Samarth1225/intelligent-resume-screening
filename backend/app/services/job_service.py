import json

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import normalize_education_requirement
from app.models.job import Job
from app.models.candidate import Candidate
from app.models.score import CandidateScore
from app.models.resume import Resume
from app.schemas.job import JobCreate, JobStats


def create_job(db: Session, payload: JobCreate) -> Job:
    job = Job(
        title=payload.title.strip(),
        description=payload.description.strip(),
        required_skills=json.dumps(payload.required_skills),
        preferred_skills=json.dumps(payload.preferred_skills),
        min_experience=payload.min_experience,
        education_requirement=payload.education_requirement,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_job(db: Session, job_id: int) -> Job | None:
    return db.query(Job).filter(Job.id == job_id).first()


def list_jobs(db: Session) -> list[Job]:
    return db.query(Job).order_by(Job.created_at.desc()).all()


def job_stats(db: Session, job_id: int) -> JobStats:
    total_candidates = db.query(func.count(Candidate.id)).filter(Candidate.job_id == job_id).scalar() or 0
    resumes_processed = (
        db.query(func.count(Resume.id))
        .join(Candidate, Resume.candidate_id == Candidate.id)
        .filter(Candidate.job_id == job_id, Resume.status == "completed")
        .scalar()
        or 0
    )
    avg_score = (
        db.query(func.avg(CandidateScore.overall_score))
        .filter(CandidateScore.job_id == job_id)
        .scalar()
    )
    above_80 = (
        db.query(func.count(CandidateScore.id))
        .filter(CandidateScore.job_id == job_id, CandidateScore.overall_score >= 80)
        .scalar()
        or 0
    )
    return JobStats(
        total_candidates=total_candidates,
        resumes_processed=resumes_processed,
        average_match_score=round(float(avg_score), 1) if avg_score else 0.0,
        candidates_above_80=above_80,
    )


def job_to_dict(job: Job) -> dict:
    """Decoded representation used by the scoring engine and API responses."""
    return {
        "id": job.id,
        "title": job.title,
        "description": job.description,
        "required_skills": json.loads(job.required_skills or "[]"),
        "preferred_skills": json.loads(job.preferred_skills or "[]"),
        "min_experience": job.min_experience,
        "education_requirement": job.education_requirement,
        "education_level": normalize_education_requirement(job.education_requirement),
    }


def job_out_payload(db: Session, job: Job) -> dict:
    data = job_to_dict(job)
    data["created_at"] = job.created_at
    data["stats"] = job_stats(db, job.id)
    return data
def delete_job(db: Session, job_id: int) -> bool:
    """Delete a job plus its candidates, scores, skills and uploaded resume files."""
    from pathlib import Path

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return False

    resumes = (
        db.query(Resume)
        .join(Candidate, Resume.candidate_id == Candidate.id)
        .filter(Candidate.job_id == job_id)
        .all()
    )
    file_paths = [r.filepath for r in resumes]

    db.delete(job)  # cascades to candidates -> resume, score, skills
    db.commit()

    for p in file_paths:
        try:
            Path(p).unlink(missing_ok=True)
        except OSError:
            pass  # a leftover file must never fail the delete
    return True