from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.candidate import Candidate
from app.routes.auth import require_demo_auth
from app.schemas.candidate import CandidateDetail
from app.services import candidate_service, resume_service

router = APIRouter(prefix="/api/candidates", tags=["candidates"], dependencies=[Depends(require_demo_auth)])


@router.get("/{candidate_id}", response_model=CandidateDetail)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    detail = candidate_service.candidate_detail(db, candidate_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return detail


@router.post("/{candidate_id}/analyze", response_model=CandidateDetail)
def analyze_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    result = resume_service.reanalyze_candidate(db, candidate)
    if result is None:
        raise HTTPException(status_code=400, detail="Candidate has no extracted resume text to re-analyze")

    return candidate_service.candidate_detail(db, candidate_id)
