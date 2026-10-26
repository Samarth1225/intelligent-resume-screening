import datetime as dt

from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # Stored as JSON-encoded lists of strings (SQLite has no native array type)
    required_skills = Column(Text, nullable=False, default="[]")
    preferred_skills = Column(Text, nullable=False, default="[]")

    min_experience = Column(Float, nullable=False, default=0)
    education_requirement = Column(String(64), nullable=False, default="Any")

    created_at = Column(DateTime, default=dt.datetime.utcnow)

    candidates = relationship("Candidate", back_populates="job", cascade="all, delete-orphan")
