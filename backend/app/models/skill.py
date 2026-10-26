from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Skill(Base):
    """One row per skill detected on a candidate's resume.

    Kept as a normalized table (rather than only the JSON blob on Candidate)
    so the /api/jobs/{id}/candidates?skills=... filter can be answered with a
    simple indexed query instead of scanning JSON text.
    """
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    name = Column(String(128), index=True, nullable=False)

    candidate = relationship("Candidate", back_populates="skill_rows")
