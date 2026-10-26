import datetime as dt

from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: str = Field(..., min_length=10)
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    min_experience: float = Field(default=0, ge=0, le=50)
    education_requirement: str = Field(default="Any")


class JobStats(BaseModel):
    total_candidates: int = 0
    resumes_processed: int = 0
    average_match_score: float = 0.0
    candidates_above_80: int = 0


class JobOut(BaseModel):
    id: int
    title: str
    description: str
    required_skills: list[str]
    preferred_skills: list[str]
    min_experience: float
    education_requirement: str
    created_at: dt.datetime
    stats: JobStats = JobStats()

    model_config = {"from_attributes": True}


class JobListItem(BaseModel):
    id: int
    title: str
    min_experience: float
    education_requirement: str
    created_at: dt.datetime
    stats: JobStats = JobStats()

    model_config = {"from_attributes": True}
