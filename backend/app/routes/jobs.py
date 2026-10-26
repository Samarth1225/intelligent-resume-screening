from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Response

from sqlalchemy.orm import Session

from app.database import get_db
from app.routes.auth import require_demo_auth
from app.schemas.job import JobCreate, JobOut, JobListItem
from app.schemas.candidate import CandidateListItem, ResumeUploadResult
from app.services import job_service, candidate_service, resume_service

router = APIRouter(prefix="/api/jobs", tags=["jobs"], dependencies=[Depends(require_demo_auth)])


@router.post("", response_model=JobOut, status_code=201)
def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    job = job_service.create_job(db, payload)
    return job_service.job_out_payload(db, job)


@router.get("", response_model=list[JobListItem])
def list_jobs(db: Session = Depends(get_db)):
    jobs = job_service.list_jobs(db)
    return [job_service.job_out_payload(db, j) for j in jobs]


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_service.job_out_payload(db, job)


@router.post("/{job_id}/resumes", response_model=list[ResumeUploadResult])
async def upload_resumes(job_id: int, files: list[UploadFile] = File(...), db: Session = Depends(get_db)):
    job = job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    results = []
    for f in files:
        raw = await f.read()
        result = resume_service.process_resume_upload(db, job, f, raw)
        results.append(result)
    return results


@router.get("/{job_id}/candidates", response_model=list[CandidateListItem])
def list_candidates(
    job_id: int,
    search: str | None = Query(default=None),
    min_score: float | None = Query(default=None, ge=0, le=100),
    skills: str | None = Query(default=None, description="Comma-separated skill names"),
    sort_by: str = Query(default="score_desc", pattern="^(score_desc|score_asc|name_asc|name_desc)$"),
    db: Session = Depends(get_db),
):
    job = job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    skill_list = [s.strip() for s in skills.split(",") if s.strip()] if skills else None
    return candidate_service.list_candidates(db, job_id, search=search, min_score=min_score,
                                              skills=skill_list, sort_by=sort_by)


@router.get("/{job_id}/rankings", response_model=list[CandidateListItem])
def get_rankings(job_id: int, db: Session = Depends(get_db)):
    job = job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return candidate_service.list_candidates(db, job_id, sort_by="score_desc")
@router.delete("/{job_id}", status_code=204)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    if not job_service.delete_job(db, job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    return Response(status_code=204)