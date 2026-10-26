import datetime as dt

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)

    filename = Column(String(255), nullable=False)
    filepath = Column(String(512), nullable=False)
    file_type = Column(String(16), nullable=False)  # "pdf" | "docx"

    # uploaded -> extracting -> analyzing -> calculating -> completed | failed
    status = Column(String(32), default="uploaded")
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=dt.datetime.utcnow)

    candidate = relationship("Candidate", back_populates="resume")
