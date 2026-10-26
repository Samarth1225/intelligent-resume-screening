import json
import logging
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.candidate import Candidate, NOT_DETECTED
from app.models.resume import Resume
from app.models.score import CandidateScore
from app.models.skill import Skill
from app.nlp.parser import extract_text, ParsingError
from app.nlp.extractor import parse_resume
from app.nlp.scoring import compute_match
from app.services.job_service import job_to_dict
from app.utils.file_handling import validate_upload, save_upload, UploadValidationError

logger = logging.getLogger(__name__)


def _persist_score(db: Session, candidate_id: int, job_id: int, result: dict) -> None:
    score = db.query(CandidateScore).filter(CandidateScore.candidate_id == candidate_id).first()
    if score is None:
        score = CandidateScore(candidate_id=candidate_id, job_id=job_id)
        db.add(score)

    score.skill_score = result["skill_score"]
    score.experience_score = result["experience_score"]
    score.education_score = result["education_score"]
    score.project_score = result["project_score"]
    score.semantic_score = result["semantic_score"]
    score.overall_score = result["overall_score"]
    score.matched_skills = json.dumps(result["matched_skills"])
    score.missing_skills = json.dumps(result["missing_skills"])
    score.explanation = json.dumps(result["explanation"])
    db.commit()


def _persist_skill_rows(db: Session, candidate_id: int, skills: list[str]) -> None:
    db.query(Skill).filter(Skill.candidate_id == candidate_id).delete()
    for name in skills:
        db.add(Skill(candidate_id=candidate_id, name=name))
    db.commit()


def process_resume_upload(db: Session, job, file: UploadFile, raw_bytes: bytes) -> dict:
    """
    Full pipeline for one uploaded file. Never raises for expected failure
    modes (bad file type, unreadable PDF, empty text, NLP errors) — instead
    returns a result dict with status "failed" and a human-readable message,
    so a batch upload of N resumes always processes the other N-1.
    """
    filename = file.filename or "resume"

    # 1. Validate + save
    try:
        ext = validate_upload(file)
        filepath = save_upload(file, raw_bytes)
    except UploadValidationError as exc:
        return {"filename": filename, "status": "failed", "candidate_id": None,
                "overall_score": None, "message": str(exc)}

    file_type = ext.lstrip(".")

    # Create Candidate + Resume rows up front so we always have a record,
    # even if extraction/parsing fails partway through.
    candidate = Candidate(job_id=job.id, name=NOT_DETECTED, email=NOT_DETECTED, phone=NOT_DETECTED)
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    resume = Resume(candidate_id=candidate.id, filename=filename, filepath=filepath,
                     file_type=file_type, status="uploaded")
    db.add(resume)
    db.commit()

    # 2. Extract raw text
    try:
        resume.status = "extracting"
        db.commit()
        text = extract_text(filepath)
    except ParsingError as exc:
        resume.status = "failed"
        resume.error_message = str(exc)
        db.commit()
        return {"filename": filename, "status": "failed", "candidate_id": candidate.id,
                "overall_score": None, "message": f"Could not extract text: {exc}"}

    if not text.strip():
        resume.status = "failed"
        resume.error_message = "No readable text found (file may be a scanned image)."
        db.commit()
        return {"filename": filename, "status": "failed", "candidate_id": candidate.id,
                "overall_score": None, "message": "No readable text found in this file."}

    # 3. NLP parsing (defensive — never let a bad resume crash the batch)
    try:
        resume.status = "analyzing"
        db.commit()
        parsed = parse_resume(text)
    except Exception as exc:  # noqa: BLE001 - deliberately broad per spec section 20
        logger.exception("NLP parsing failed for %s", filename)
        parsed = {
            "name": None, "email": None, "phone": None, "education": None,
            "education_level": 0, "experience_years": None, "experience_text": None,
            "skills": [], "projects_text": None, "certifications": [],
        }
        resume.error_message = f"Partial parse only ({exc})"

    candidate.name = parsed["name"] or NOT_DETECTED
    candidate.email = parsed["email"] or NOT_DETECTED
    candidate.phone = parsed["phone"] or NOT_DETECTED
    candidate.education = parsed["education"] or NOT_DETECTED
    candidate.education_level = parsed["education_level"]
    candidate.experience_years = parsed["experience_years"]
    candidate.experience_text = parsed["experience_text"] or NOT_DETECTED
    candidate.skills = json.dumps(parsed["skills"])
    candidate.projects_text = parsed["projects_text"] or NOT_DETECTED
    candidate.certifications = json.dumps(parsed["certifications"])
    candidate.raw_text = text
    db.commit()

    _persist_skill_rows(db, candidate.id, parsed["skills"])

    # 4. Scoring
    try:
        resume.status = "calculating"
        db.commit()
        job_dict = job_to_dict(job)
        result = compute_match(job_dict, parsed, text)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Scoring failed for candidate %s", candidate.id)
        resume.status = "failed"
        resume.error_message = f"Scoring failed: {exc}"
        db.commit()
        return {"filename": filename, "status": "failed", "candidate_id": candidate.id,
                "overall_score": None, "message": "Resume parsed but scoring failed."}

    _persist_score(db, candidate.id, job.id, result)

    resume.status = "completed"
    resume.error_message = None
    db.commit()

    return {
        "filename": filename,
        "status": "completed",
        "candidate_id": candidate.id,
        "overall_score": result["overall_score"],
        "message": None,
    }


def reanalyze_candidate(db: Session, candidate: Candidate) -> dict | None:
    """Re-run scoring for an existing candidate (e.g. after job requirements
    changed), reusing the already-extracted raw text — no re-upload needed."""
    job = candidate.job
    if job is None or not candidate.raw_text:
        return None

    parsed = {
        "name": candidate.name,
        "email": candidate.email,
        "phone": candidate.phone,
        "education": candidate.education,
        "education_level": candidate.education_level,
        "experience_years": candidate.experience_years,
        "experience_text": candidate.experience_text,
        "skills": json.loads(candidate.skills or "[]"),
        "projects_text": candidate.projects_text,
        "certifications": json.loads(candidate.certifications or "[]"),
    }
    job_dict = job_to_dict(job)
    result = compute_match(job_dict, parsed, candidate.raw_text)
    _persist_score(db, candidate.id, job.id, result)
    return result
