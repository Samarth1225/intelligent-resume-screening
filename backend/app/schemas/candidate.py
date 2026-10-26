import datetime as dt

from pydantic import BaseModel


class ExplanationPoint(BaseModel):
    type: str  # "+" or "-"
    text: str


class ScoreBreakdown(BaseModel):
    skill_score: float = 0
    experience_score: float = 0
    education_score: float = 0
    project_score: float = 0
    semantic_score: float = 0
    overall_score: float = 0
    matched_skills: list[str] = []
    missing_skills: list[str] = []
    explanation: list[ExplanationPoint] = []


class CandidateListItem(BaseModel):
    id: int
    rank: int | None = None
    name: str
    email: str
    phone: str
    skills: list[str] = []
    experience_years: float | None = None
    overall_score: float = 0
    status_label: str = "Weak"
    skills_matched_label: str = "0 / 0"
    resume_status: str = "uploaded"

    model_config = {"from_attributes": True}


class CandidateDetail(BaseModel):
    id: int
    job_id: int
    name: str
    email: str
    phone: str
    education: str
    experience_years: float | None
    experience_text: str
    skills: list[str]
    projects_text: str
    certifications: list[str]
    resume_status: str
    resume_filename: str | None = None
    created_at: dt.datetime
    score: ScoreBreakdown

    model_config = {"from_attributes": True}


class ResumeUploadResult(BaseModel):
    filename: str
    status: str  # "completed" | "failed"
    candidate_id: int | None = None
    overall_score: float | None = None
    message: str | None = None
