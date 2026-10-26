import datetime as dt

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base

NOT_DETECTED = "Not detected"


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)

    name = Column(String(255), default=NOT_DETECTED)
    email = Column(String(255), default=NOT_DETECTED)
    phone = Column(String(64), default=NOT_DETECTED)

    education = Column(Text, default=NOT_DETECTED)
    education_level = Column(Integer, default=0)  # ordinal, see config.EDUCATION_LEVELS

    experience_years = Column(Float, nullable=True)  # None => not detected
    experience_text = Column(Text, default=NOT_DETECTED)

    skills = Column(Text, default="[]")          # JSON list of extracted canonical skills
    projects_text = Column(Text, default=NOT_DETECTED)
    certifications = Column(Text, default="[]")   # JSON list

    raw_text = Column(Text, default="")  # full extracted resume text, used for re-analysis

    created_at = Column(DateTime, default=dt.datetime.utcnow)

    job = relationship("Job", back_populates="candidates")
    resume = relationship("Resume", back_populates="candidate", uselist=False, cascade="all, delete-orphan")
    score = relationship("CandidateScore", back_populates="candidate", uselist=False, cascade="all, delete-orphan")
    skill_rows = relationship("Skill", back_populates="candidate", cascade="all, delete-orphan")
