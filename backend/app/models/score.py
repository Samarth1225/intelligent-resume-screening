import datetime as dt

from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class CandidateScore(Base):
    __tablename__ = "candidate_scores"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, unique=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)

    skill_score = Column(Float, default=0)
    experience_score = Column(Float, default=0)
    education_score = Column(Float, default=0)
    project_score = Column(Float, default=0)
    semantic_score = Column(Float, default=0)
    overall_score = Column(Float, default=0)

    matched_skills = Column(Text, default="[]")   # JSON list
    missing_skills = Column(Text, default="[]")   # JSON list
    explanation = Column(Text, default="[]")       # JSON list of {"type": "+"/"-", "text": "..."}

    updated_at = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

    candidate = relationship("Candidate", back_populates="score")
