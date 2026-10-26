"""
Populates the database with sample jobs and candidates so the app is
immediately demonstrable after installation (spec section 18).

Runs the sample resumes through the exact same parsing/scoring pipeline the
API uses (app.services.resume_service.process_resume_upload) — this is not
a shortcut that fakes scores, it's the real thing.

Usage:
    python seed_data.py            # seed (skips if jobs already exist)
    python seed_data.py --reset    # wipe the DB file and reseed from scratch
"""
import sys
from pathlib import Path

from app.database import Base, engine, SessionLocal
from app import models  # noqa: F401
from app.models.job import Job
from app.schemas.job import JobCreate
from app.services import job_service, resume_service

RESUME_DIR = Path(__file__).resolve().parent.parent / "sample_data" / "resumes"


class _FakeUploadFile:
    """Minimal stand-in for fastapi.UploadFile — process_resume_upload only
    reads the .filename attribute (the bytes are passed separately)."""
    def __init__(self, filename: str):
        self.filename = filename


def _upload(db, job, filename: str):
    path = RESUME_DIR / filename
    if not path.exists():
        print(f"  ! Missing sample file: {path} (run generate_sample_files.py first)")
        return
    raw_bytes = path.read_bytes()
    result = resume_service.process_resume_upload(db, job, _FakeUploadFile(filename), raw_bytes)
    status_icon = "OK" if result["status"] == "completed" else "FAIL"
    score = f"{result['overall_score']}%" if result["overall_score"] is not None else "-"
    print(f"  [{status_icon}] {filename:<32} score={score:<8} {result['message'] or ''}")


def seed(db) -> None:
    print("Creating job: Java Backend Developer")
    job1 = job_service.create_job(db, JobCreate(
        title="Java Backend Developer",
        description=(
            "We are looking for a Java Backend Developer to design and build scalable REST APIs "
            "for our fintech platform. You will work with Spring Boot, SQL databases, and modern "
            "DevOps tooling in an agile team."
        ),
        required_skills=["Java", "Spring Boot", "SQL", "REST API", "Git"],
        preferred_skills=["Docker", "AWS"],
        min_experience=2,
        education_requirement="Bachelor's",
    ))
    for filename in [
        "ananya_rao_resume.pdf",
        "karan_mehta_resume.docx",
        "priya_nair_resume.pdf",
        "suresh_iyer_resume.docx",
    ]:
        _upload(db, job1, filename)

    print("\nCreating job: Data Analyst / ML Engineer")
    job2 = job_service.create_job(db, JobCreate(
        title="Data Analyst / ML Engineer",
        description=(
            "We are hiring a Data Analyst to build machine learning models and dashboards that "
            "drive product decisions. You will work with Python, pandas, SQL, and visualization "
            "tools to turn data into insight."
        ),
        required_skills=["Python", "Machine Learning", "Pandas", "SQL", "Data Analysis"],
        preferred_skills=["TensorFlow", "Power BI"],
        min_experience=1,
        education_requirement="Bachelor's",
    ))
    for filename in [
        "neha_kulkarni_resume.pdf",
        "priya_nair_resume.pdf",
        "ananya_rao_resume.pdf",
    ]:
        _upload(db, job2, filename)

    print("\nSeed complete.")


def main():
    if "--reset" in sys.argv:
        db_path = Path(__file__).resolve().parent / "resume_screening.db"
        if db_path.exists():
            db_path.unlink()
            print(f"Deleted {db_path}")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Job).count() > 0 and "--reset" not in sys.argv:
            print("Database already has jobs — skipping seed (use --reset to reseed).")
            return
        seed(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
